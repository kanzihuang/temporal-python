import ssl
import logging
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from typing import Optional
from temporal_python.shared.config import config
from temporal_python.shared.schemas import VMRequest

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(config.logging.level)
file_handler = logging.FileHandler(config.logging.file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class VMwareService:
    def __init__(self):
        self.connection = None
        self.content = None

    def connect(self) -> None:
        """连接到VMware vCenter服务器"""
        try:
            # 禁用SSL验证（生产环境建议启用证书验证）
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            self.connection = SmartConnect(
                host=config.vmware.host,
                user=config.vmware.username,
                pwd=config.vmware.password,
                port=config.vmware.port,
                sslContext=context
            )

            if not self.connection:
                raise Exception("无法连接到VMware vCenter服务器")

            self.content = self.connection.RetrieveContent()
            logger.info(f"成功连接到VMware vCenter: {config.vmware.host}")

        except Exception as e:
            logger.error(f"VMware连接失败: {str(e)}")
            raise

    def _get_resource_pool(self) -> vim.ResourcePool:
        """获取资源池"""
        datacenter = self._get_datacenter()
        cluster = self._get_cluster(datacenter)
        return cluster.resourcePool

    def _get_datacenter(self) -> vim.Datacenter:
        """获取数据中心"""
        for dc in self.content.rootFolder.childEntity:
            if dc.name == config.vmware.datacenter:
                return dc
        raise Exception(f"数据中心 {config.vmware.datacenter} 未找到")

    def _get_cluster(self, datacenter: vim.Datacenter) -> vim.ClusterComputeResource:
        """获取集群"""
        for cluster in datacenter.hostFolder.childEntity:
            if cluster.name == config.vmware.cluster:
                return cluster
        raise Exception(f"集群 {config.vmware.cluster} 未找到")

    def _get_datastore(self) -> vim.Datastore:
        """获取数据存储"""
        datastores = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Datastore], True
        ).view
        for ds in datastores:
            if ds.name == config.vmware.datastore:
                return ds
        raise Exception(f"数据存储 {config.vmware.datastore} 未找到")

    def _get_network(self) -> vim.Network:
        """获取网络"""
        networks = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Network], True
        ).view
        for net in networks:
            if net.name == config.vmware.network:
                return net
        raise Exception(f"网络 {config.vmware.network} 未找到")

    def _get_vm_folder(self) -> vim.Folder:
        """获取VM文件夹"""
        # 解析文件夹路径
        path_parts = config.vmware.folder.strip('/').split('/')
        current_folder = self.content.rootFolder

        for part in path_parts:
            found = False
            for child in current_folder.childEntity:
                if isinstance(child, vim.Folder) and child.name == part:
                    current_folder = child
                    found = True
                    break
            if not found:
                raise Exception(f"文件夹路径 {config.vmware.folder} 未找到")
        return current_folder

    def create_vm(self, request: VMRequest) -> str:
        """创建虚拟机"""
        if not self.connection:
            self.connect()

        try:
            # 获取必要的资源
            resource_pool = self._get_resource_pool()
            datastore = self._get_datastore()
            network = self._get_network()
            vm_folder = self._get_vm_folder()

            # 创建VM配置规范
            vm_config = vim.vm.ConfigSpec()
            vm_config.name = request.vm_name
            vm_config.guestId = request.guest_id
            vm_config.numCPUs = request.num_cpus
            vm_config.memoryMB = request.memory_gb * 1024  # 转换为MB
            vm_config.annotation = request.notes or ""

            # 创建磁盘规范
            disk_spec = vim.vm.device.VirtualDeviceSpec()
            disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            disk_spec.device = vim.vm.device.VirtualDisk()
            disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
            disk_spec.device.backing.diskMode = "persistent"
            disk_spec.device.backing.thinProvisioned = True
            disk_spec.device.backing.datastore = datastore
            disk_spec.device.unitNumber = 0
            disk_spec.device.capacityInKB = request.disk_size_gb * 1024 * 1024  # 转换为KB

            # 创建网络适配器规范
            nic_spec = vim.vm.device.VirtualDeviceSpec()
            nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            nic_spec.device = vim.vm.device.VirtualE1000()
            nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
            nic_spec.device.backing.network = network
            nic_spec.device.backing.deviceName = network.name
            nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
            nic_spec.device.connectable.startConnected = True
            nic_spec.device.unitNumber = 1

            # 添加设备到配置
            vm_config.deviceChange = [disk_spec, nic_spec]

            # 创建VM任务
            task = vm_folder.CreateVM_Task(
                config=vm_config,
                pool=resource_pool
            )

            # 等待任务完成
            task_result = self._wait_for_task(task)
            if task_result != vim.TaskInfo.State.success:
                raise Exception(f"创建VM失败: {task.info.error.msg}")

            logger.info(f"虚拟机 {request.vm_name} 创建成功")

            # 如果需要开机
            if request.power_on:
                vm = self._get_vm_by_name(request.vm_name)
                power_task = vm.PowerOnVM_Task()
                self._wait_for_task(power_task)
                logger.info(f"虚拟机 {request.vm_name} 已开机")

            return request.vm_name

        except Exception as e:
            logger.error(f"创建虚拟机失败: {str(e)}")
            raise
        finally:
            Disconnect(self.connection)

    def _get_vm_by_name(self, vm_name: str) -> vim.VirtualMachine:
        """通过名称查找虚拟机"""
        vm_view = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        for vm in vm_view.view:
            if vm.name == vm_name:
                return vm
        raise Exception(f"虚拟机 {vm_name} 未找到")

    @staticmethod
    def _wait_for_task(task: vim.Task) -> vim.TaskInfo.State:
        """等待任务完成"""
        import time
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(2)
        return task.info.state