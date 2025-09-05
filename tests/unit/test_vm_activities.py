"""
Unit tests for temporal_python.activities.vm_activities module.
"""
import pytest
from unittest.mock import Mock, patch
from temporal_python.activities.vm_activities import create_vm_activity
from temporal_python.shared.schemas import VMRequest


class TestVMActivities:
    """Test VM creation activities."""

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_success(self, mock_logger, mock_vmware_service_class, sample_vm_request):
        """测试成功创建VM活动"""
        # 模拟VMwareService
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.return_value = "test-vm-01"
        mock_vmware_service_class.return_value = mock_vmware_service

        # 执行活动
        result = await create_vm_activity(sample_vm_request)

        # 验证结果
        assert result == "test-vm-01"

        # 验证VMwareService被正确调用
        mock_vmware_service_class.assert_called_once()
        mock_vmware_service.create_vm.assert_called_once_with(sample_vm_request)

        # 验证日志记录
        mock_logger.info.assert_any_call(f"开始创建虚拟机: {sample_vm_request.vm_name}")
        mock_logger.info.assert_any_call("虚拟机创建活动完成: test-vm-01")

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_failure(self, mock_logger, mock_vmware_service_class, sample_vm_request):
        """测试VM创建活动失败"""
        # 模拟VMwareService抛出异常
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.side_effect = Exception("VMware connection failed")
        mock_vmware_service_class.return_value = mock_vmware_service

        # 执行活动并验证异常
        with pytest.raises(Exception) as exc_info:
            await create_vm_activity(sample_vm_request)

        # 验证异常信息
        assert "创建虚拟机失败: VMware connection failed" in str(exc_info.value)

        # 验证日志记录
        mock_logger.info.assert_called_once_with(f"开始创建虚拟机: {sample_vm_request.vm_name}")
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert "虚拟机创建活动失败" in error_call[0][0]
        assert error_call[1]['exc_info'] is True

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_with_different_vm_names(self, mock_logger, mock_vmware_service_class):
        """测试不同VM名称的创建活动"""
        vm_names = ["test-vm-01", "prod-server-01", "dev-env-02"]

        for vm_name in vm_names:
            # 创建请求
            request = VMRequest(
                vm_name=vm_name,
                num_cpus=2,
                memory_gb=4,
                disk_size_gb=40
            )

            # 模拟VMwareService
            mock_vmware_service = Mock()
            mock_vmware_service.create_vm.return_value = vm_name
            mock_vmware_service_class.return_value = mock_vmware_service

            # 执行活动
            result = await create_vm_activity(request)

            # 验证结果
            assert result == vm_name
            mock_vmware_service.create_vm.assert_called_once_with(request)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_with_different_configurations(self, mock_logger, mock_vmware_service_class):
        """测试不同配置的VM创建活动"""
        configurations = [
            {"num_cpus": 1, "memory_gb": 2, "disk_size_gb": 20},
            {"num_cpus": 4, "memory_gb": 8, "disk_size_gb": 100},
            {"num_cpus": 8, "memory_gb": 16, "disk_size_gb": 500},
        ]

        for config in configurations:
            # 创建请求
            request = VMRequest(
                vm_name="test-vm",
                **config
            )

            # 模拟VMwareService
            mock_vmware_service = Mock()
            mock_vmware_service.create_vm.return_value = "test-vm"
            mock_vmware_service_class.return_value = mock_vmware_service

            # 执行活动
            result = await create_vm_activity(request)

            # 验证结果
            assert result == "test-vm"
            mock_vmware_service.create_vm.assert_called_once_with(request)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_with_notes(self, mock_logger, mock_vmware_service_class):
        """测试带注释的VM创建活动"""
        request = VMRequest(
            vm_name="test-vm-01",
            num_cpus=2,
            memory_gb=4,
            disk_size_gb=40,
            notes="This is a test VM created by unit test"
        )

        # 模拟VMwareService
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.return_value = "test-vm-01"
        mock_vmware_service_class.return_value = mock_vmware_service

        # 执行活动
        result = await create_vm_activity(request)

        # 验证结果
        assert result == "test-vm-01"
        mock_vmware_service.create_vm.assert_called_once_with(request)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_without_power_on(self, mock_logger, mock_vmware_service_class):
        """测试不自动开机的VM创建活动"""
        request = VMRequest(
            vm_name="test-vm-01",
            num_cpus=2,
            memory_gb=4,
            disk_size_gb=40,
            power_on=False
        )

        # 模拟VMwareService
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.return_value = "test-vm-01"
        mock_vmware_service_class.return_value = mock_vmware_service

        # 执行活动
        result = await create_vm_activity(request)

        # 验证结果
        assert result == "test-vm-01"
        mock_vmware_service.create_vm.assert_called_once_with(request)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_vmware_service_exception(self, mock_logger, mock_vmware_service_class, sample_vm_request):
        """测试VMwareService抛出特定异常"""
        # 模拟不同类型的异常
        exceptions = [
            Exception("Network timeout"),
            Exception("Authentication failed"),
            Exception("Insufficient resources"),
            Exception("VM already exists")
        ]

        for exception in exceptions:
            # 模拟VMwareService抛出异常
            mock_vmware_service = Mock()
            mock_vmware_service.create_vm.side_effect = exception
            mock_vmware_service_class.return_value = mock_vmware_service

            # 执行活动并验证异常
            with pytest.raises(Exception) as exc_info:
                await create_vm_activity(sample_vm_request)

            # 验证异常信息包含原始异常
            assert str(exception) in str(exc_info.value)
            assert "创建虚拟机失败" in str(exc_info.value)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_logging_levels(self, mock_logger, mock_vmware_service_class, sample_vm_request):
        """测试不同日志级别的记录"""
        # 模拟成功情况
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.return_value = "test-vm-01"
        mock_vmware_service_class.return_value = mock_vmware_service

        # 执行活动
        await create_vm_activity(sample_vm_request)

        # 验证info日志调用
        info_calls = mock_logger.info.call_args_list
        assert len(info_calls) == 2
        assert "开始创建虚拟机" in info_calls[0][0][0]
        assert "虚拟机创建活动完成" in info_calls[1][0][0]

        # 验证没有error日志调用
        mock_logger.error.assert_not_called()

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.activities.vm_activities.logger')
    async def test_create_vm_activity_error_logging(self, mock_logger, mock_vmware_service_class, sample_vm_request):
        """测试错误日志记录"""
        # 模拟失败情况
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.side_effect = Exception("Test error")
        mock_vmware_service_class.return_value = mock_vmware_service

        # 执行活动
        with pytest.raises(Exception):
            await create_vm_activity(sample_vm_request)

        # 验证error日志调用
        error_calls = mock_logger.error.call_args_list
        assert len(error_calls) == 1
        assert "虚拟机创建活动失败" in error_calls[0][0][0]
        assert error_calls[0][1]['exc_info'] is True