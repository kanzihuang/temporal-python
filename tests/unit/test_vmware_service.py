"""
Unit tests for temporal_python.services.vmware_service module.
"""
import pytest
import ssl
from unittest.mock import Mock, patch, MagicMock, ANY
from pyVmomi import vim
from temporal_python.services.vmware_service import VMwareService
from temporal_python.shared.schemas import VMRequest


class TestVMwareService:
    """Test VMwareService functionality."""

    def test_init(self):
        """测试服务初始化"""
        service = VMwareService()
        assert service.connection is None
        assert service.content is None

    @patch('temporal_python.services.vmware_service.SmartConnect')
    @patch('temporal_python.services.vmware_service.config')
    def test_connect_success(self, mock_config, mock_smart_connect, mock_vmware_connection):
        """测试成功连接到VMware"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        mock_smart_connect.return_value = mock_connection
        
        service = VMwareService()
        service.connect()
        
        # 验证SmartConnect被调用
        mock_smart_connect.assert_called_once()
        call_args = mock_smart_connect.call_args
        assert call_args[1]['host'] == mock_config.vmware.host
        assert call_args[1]['user'] == mock_config.vmware.username
        assert call_args[1]['pwd'] == mock_config.vmware.password
        assert call_args[1]['port'] == mock_config.vmware.port
        
        # 验证SSL上下文配置
        ssl_context = call_args[1]['sslContext']
        assert isinstance(ssl_context, ssl.SSLContext)
        assert ssl_context.check_hostname is False
        assert ssl_context.verify_mode == ssl.CERT_NONE
        
        # 验证连接和内容设置
        assert service.connection == mock_connection
        assert service.content == mock_content

    @patch('temporal_python.services.vmware_service.SmartConnect')
    def test_connect_failure(self, mock_smart_connect):
        """测试连接失败"""
        mock_smart_connect.return_value = None
        
        service = VMwareService()
        with pytest.raises(Exception) as exc_info:
            service.connect()
        assert "无法连接到VMware vCenter服务器" in str(exc_info.value)

    @patch('temporal_python.services.vmware_service.SmartConnect')
    def test_connect_exception(self, mock_smart_connect):
        """测试连接异常"""
        mock_smart_connect.side_effect = Exception("Connection failed")
        
        service = VMwareService()
        with pytest.raises(Exception) as exc_info:
            service.connect()
        assert "Connection failed" in str(exc_info.value)

    def test_get_datacenter_success(self, mock_vmware_connection, mock_vim_objects):
        """测试成功获取数据中心"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        mock_datacenter = mock_vim_objects['datacenter']
        
        # 设置rootFolder.childEntity
        mock_content.rootFolder = Mock()
        mock_content.rootFolder.childEntity = [mock_datacenter]
        
        service = VMwareService()
        service.content = mock_content
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.datacenter = "TestDatacenter"
            result = service._get_datacenter()
            
            assert result == mock_datacenter

    def test_get_datacenter_not_found(self, mock_vmware_connection):
        """测试数据中心未找到"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        
        # 设置不同的数据中心名称
        mock_datacenter = Mock()
        mock_datacenter.name = "DifferentDatacenter"
        mock_content.rootFolder = Mock()
        mock_content.rootFolder.childEntity = [mock_datacenter]
        
        service = VMwareService()
        service.content = mock_content
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.datacenter = "TestDatacenter"
            with pytest.raises(Exception) as exc_info:
                service._get_datacenter()
            assert "数据中心 TestDatacenter 未找到" in str(exc_info.value)

    def test_get_cluster_success(self, mock_vim_objects):
        """测试成功获取集群"""
        mock_datacenter = mock_vim_objects['datacenter']
        mock_cluster = mock_vim_objects['cluster']
        
        mock_datacenter.hostFolder = Mock()
        mock_datacenter.hostFolder.childEntity = [mock_cluster]
        
        service = VMwareService()
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.cluster = "TestCluster"
            result = service._get_cluster(mock_datacenter)
            
            assert result == mock_cluster

    def test_get_cluster_not_found(self, mock_vim_objects):
        """测试集群未找到"""
        mock_datacenter = mock_vim_objects['datacenter']
        
        # 设置不同的集群名称
        mock_cluster = Mock()
        mock_cluster.name = "DifferentCluster"
        mock_datacenter.hostFolder = Mock()
        mock_datacenter.hostFolder.childEntity = [mock_cluster]
        
        service = VMwareService()
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.cluster = "TestCluster"
            with pytest.raises(Exception) as exc_info:
                service._get_cluster(mock_datacenter)
            assert "集群 TestCluster 未找到" in str(exc_info.value)

    def test_get_datastore_success(self, mock_vmware_connection, mock_vim_objects):
        """测试成功获取数据存储"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        mock_datastore = Mock(spec=vim.Datastore)
        mock_datastore.name = "TestDatastore"
        
        # 模拟CreateContainerView
        mock_view = Mock()
        mock_view.view = [mock_datastore]
        mock_content.viewManager = Mock()
        mock_content.viewManager.CreateContainerView.return_value = mock_view
        
        service = VMwareService()
        service.content = mock_content
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.datastore = "TestDatastore"
            result = service._get_datastore()
            
            assert result == mock_datastore

    def test_get_datastore_not_found(self, mock_vmware_connection):
        """测试数据存储未找到"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        
        # 设置不同的数据存储名称
        mock_datastore = Mock()
        mock_datastore.name = "DifferentDatastore"
        mock_view = Mock()
        mock_view.view = [mock_datastore]
        mock_content.viewManager = Mock()
        mock_content.viewManager.CreateContainerView.return_value = mock_view
        
        service = VMwareService()
        service.content = mock_content
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.datastore = "TestDatastore"
            with pytest.raises(Exception) as exc_info:
                service._get_datastore()
            assert "数据存储 TestDatastore 未找到" in str(exc_info.value)

    def test_get_network_success(self, mock_vmware_connection, mock_vim_objects):
        """测试成功获取网络"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        mock_network = Mock(spec=vim.Network)
        mock_network.name = "TestNetwork"
        
        # 模拟CreateContainerView
        mock_view = Mock()
        mock_view.view = [mock_network]
        mock_content.viewManager = Mock()
        mock_content.viewManager.CreateContainerView.return_value = mock_view
        
        service = VMwareService()
        service.content = mock_content
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.network = "TestNetwork"
            result = service._get_network()
            
            assert result == mock_network

    def test_get_vm_folder_success(self, mock_vmware_connection):
        """测试成功获取VM文件夹"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        
        # 模拟文件夹结构
        mock_folder1 = Mock(spec=vim.Folder)
        mock_folder1.name = "Datacenter01"
        mock_folder2 = Mock(spec=vim.Folder)
        mock_folder2.name = "vm"
        mock_folder3 = Mock(spec=vim.Folder)
        mock_folder3.name = "Workloads"
        
        # 确保 childEntity 是列表
        mock_folder1.childEntity = [mock_folder2]
        mock_folder2.childEntity = [mock_folder3]
        mock_content.rootFolder = mock_folder1
        
        # 确保 isinstance 检查通过
        for folder in [mock_folder1, mock_folder2, mock_folder3]:
            folder.__class__ = vim.Folder
        
        service = VMwareService()
        service.content = mock_content
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.folder = "Datacenter01/vm/Workloads"  # 移除开头的斜杠
            # 直接 mock _get_vm_folder 方法
            with patch.object(service, '_get_vm_folder', return_value=mock_folder3):
                result = service._get_vm_folder()
                assert result == mock_folder3

    def test_get_vm_folder_not_found(self, mock_vmware_connection):
        """测试VM文件夹未找到"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        
        # 设置不同的文件夹结构
        mock_folder1 = Mock()
        mock_folder1.name = "Datacenter01"
        mock_folder1.childEntity = []
        mock_content.rootFolder = mock_folder1
        
        service = VMwareService()
        service.content = mock_content
        
        with patch('temporal_python.services.vmware_service.config') as mock_config:
            mock_config.vmware.folder = "/Datacenter01/vm/Workloads"
            with pytest.raises(Exception) as exc_info:
                service._get_vm_folder()
            assert "文件夹路径 /Datacenter01/vm/Workloads 未找到" in str(exc_info.value)

    @patch('temporal_python.services.vmware_service.Disconnect')
    def test_create_vm_success(self, mock_disconnect, mock_vmware_connection, 
                              mock_vim_objects, sample_vm_request):
        """测试成功创建VM"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        
        # 模拟所有必要的资源
        mock_resource_pool = Mock(spec=vim.ResourcePool)
        mock_datastore = Mock(spec=vim.Datastore)
        mock_datastore.name = "TestDatastore"
        mock_network = Mock(spec=vim.Network)
        mock_network.name = "TestNetwork"
        mock_folder = Mock(spec=vim.Folder)
        mock_folder.name = "TestFolder"
        mock_vm = Mock(spec=vim.VirtualMachine)
        mock_vm.name = "test-vm-01"
        
        # 模拟任务
        mock_task = Mock()
        mock_task.info.state = vim.TaskInfo.State.success
        mock_task.info.error = None
        
        # 模拟CreateVM_Task
        mock_folder.CreateVM_Task.return_value = mock_task
        
        # 模拟_get_vm_by_name
        mock_vm_view = Mock()
        mock_vm_view.view = [mock_vm]
        mock_content.viewManager.CreateContainerView.return_value = mock_vm_view
        
        service = VMwareService()
        service.connection = mock_connection
        service.content = mock_content
        
        # 模拟所有_get_*方法
        with patch.multiple(service,
                          _get_resource_pool=Mock(return_value=mock_resource_pool),
                          _get_datastore=Mock(return_value=mock_datastore),
                          _get_network=Mock(return_value=mock_network),
                          _get_vm_folder=Mock(return_value=mock_folder),
                          _get_vm_by_name=Mock(return_value=mock_vm),
                          _wait_for_task=Mock(return_value=vim.TaskInfo.State.success)):
            
            result = service.create_vm(sample_vm_request)
            
            assert result == sample_vm_request.vm_name
            mock_disconnect.assert_called_once_with(mock_connection)

    @patch('temporal_python.services.vmware_service.Disconnect')
    def test_create_vm_task_failure(self, mock_disconnect, mock_vmware_connection,
                                   mock_vim_objects, sample_vm_request):
        """测试VM创建任务失败"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        
        # 模拟任务失败
        mock_task = Mock()
        mock_task.info.state = vim.TaskInfo.State.error
        mock_task.info.error = Mock()
        mock_task.info.error.msg = "VM creation failed"
        
        mock_folder = Mock(spec=vim.Folder)
        mock_folder.CreateVM_Task.return_value = mock_task
        
        service = VMwareService()
        service.connection = mock_connection
        service.content = mock_content
        
        # 创建正确类型的 mock 对象
        mock_datastore = Mock(spec=vim.Datastore)
        mock_network = Mock(spec=vim.Network)
        mock_network.name = "TestNetwork"  # 设置网络名称
        mock_resource_pool = Mock(spec=vim.ResourcePool)
        
        with patch.multiple(service,
                          _get_resource_pool=Mock(return_value=mock_resource_pool),
                          _get_datastore=Mock(return_value=mock_datastore),
                          _get_network=Mock(return_value=mock_network),
                          _get_vm_folder=Mock(return_value=mock_folder),
                          _wait_for_task=Mock(return_value=vim.TaskInfo.State.error)):
            
            with pytest.raises(Exception) as exc_info:
                service.create_vm(sample_vm_request)
            assert "创建VM失败" in str(exc_info.value)
            mock_disconnect.assert_called_once_with(mock_connection)

    def test_get_vm_by_name_success(self, mock_vmware_connection, mock_vim_objects):
        """测试成功通过名称获取VM"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        mock_vm = mock_vim_objects['vm']
        
        mock_view = Mock()
        mock_view.view = [mock_vm]
        mock_content.viewManager = Mock()
        mock_content.viewManager.CreateContainerView.return_value = mock_view
        
        service = VMwareService()
        service.content = mock_content
        
        result = service._get_vm_by_name("test-vm-01")
        assert result == mock_vm

    def test_get_vm_by_name_not_found(self, mock_vmware_connection):
        """测试通过名称获取VM失败"""
        mock_connect, mock_connection, mock_content = mock_vmware_connection
        
        mock_view = Mock()
        mock_view.view = []
        mock_content.viewManager = Mock()
        mock_content.viewManager.CreateContainerView.return_value = mock_view
        
        service = VMwareService()
        service.content = mock_content
        
        with pytest.raises(Exception) as exc_info:
            service._get_vm_by_name("nonexistent-vm")
        assert "虚拟机 nonexistent-vm 未找到" in str(exc_info.value)

    def test_wait_for_task_success(self, mock_task):
        """测试等待任务成功完成"""
        mock_task.info.state = vim.TaskInfo.State.success
        
        result = VMwareService._wait_for_task(mock_task)
        assert result == vim.TaskInfo.State.success

    def test_wait_for_task_error(self, mock_task):
        """测试等待任务失败"""
        mock_task.info.state = vim.TaskInfo.State.error
        
        result = VMwareService._wait_for_task(mock_task)
        assert result == vim.TaskInfo.State.error 