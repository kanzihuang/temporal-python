"""
Integration tests for VM creation workflow and activities.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from temporal_python.workflows.vm_workflows import VMCreationWorkflow
from temporal_python.activities.vm_activities import create_vm_activity
from temporal_python.shared.schemas import VMRequest


class TestVMCreationIntegration:
    """Integration tests for VM creation workflow and activities."""

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_full_workflow_to_activity_integration(self, mock_execute_activity, mock_vmware_service_class, sample_vm_request):
        """测试完整的工作流到活动集成"""
        # 模拟VMwareService
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.return_value = "test-vm-01"
        mock_vmware_service_class.return_value = mock_vmware_service

        # 模拟工作流执行活动
        mock_execute_activity.return_value = "test-vm-01"

        # 创建工作流实例
        workflow = VMCreationWorkflow()

        # 执行工作流
        workflow_result = await workflow.run(sample_vm_request)

        # 验证工作流结果
        assert workflow_result == "test-vm-01"

        # 验证工作流调用了活动
        mock_execute_activity.assert_called_once()

        # 直接测试活动
        activity_result = await create_vm_activity(sample_vm_request)

        # 验证活动结果
        assert activity_result == "test-vm-01"

        # 验证VMwareService被正确调用
        mock_vmware_service.create_vm.assert_called_with(sample_vm_request)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_integration_with_different_vm_configurations(self, mock_execute_activity, mock_vmware_service_class):
        """测试不同VM配置的集成"""
        configurations = [
            {
                "vm_name": "small-vm",
                "num_cpus": 1,
                "memory_gb": 2,
                "disk_size_gb": 20
            },
            {
                "vm_name": "medium-vm",
                "num_cpus": 4,
                "memory_gb": 8,
                "disk_size_gb": 100
            },
            {
                "vm_name": "large-vm",
                "num_cpus": 8,
                "memory_gb": 16,
                "disk_size_gb": 500
            }
        ]

        for config in configurations:
            # 创建请求
            request = VMRequest(**config)

            # 模拟VMwareService
            mock_vmware_service = Mock()
            mock_vmware_service.create_vm.return_value = config["vm_name"]
            mock_vmware_service_class.return_value = mock_vmware_service

            # 模拟工作流执行
            mock_execute_activity.return_value = config["vm_name"]

            # 执行工作流
            workflow = VMCreationWorkflow()
            workflow_result = await workflow.run(request)

            # 执行活动
            activity_result = await create_vm_activity(request)

            # 验证结果一致
            assert workflow_result == activity_result == config["vm_name"]
            mock_vmware_service.create_vm.assert_called_with(request)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_integration_error_handling(self, mock_execute_activity, mock_vmware_service_class, sample_vm_request):
        """测试集成错误处理"""
        # 模拟VMwareService抛出异常
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.side_effect = Exception("Integration test error")
        mock_vmware_service_class.return_value = mock_vmware_service

        # 模拟工作流执行活动时抛出异常
        mock_execute_activity.side_effect = Exception("Activity execution failed")

        # 测试工作流错误处理
        workflow = VMCreationWorkflow()
        with pytest.raises(Exception) as exc_info:
            await workflow.run(sample_vm_request)
        assert "Activity execution failed" in str(exc_info.value)

        # 测试活动错误处理
        with pytest.raises(Exception) as exc_info:
            await create_vm_activity(sample_vm_request)
        assert "创建虚拟机失败: Integration test error" in str(exc_info.value)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_integration_retry_mechanism(self, mock_execute_activity, mock_vmware_service_class, sample_vm_request):
        """测试集成重试机制"""
        # 模拟VMwareService第一次失败，第二次成功
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.side_effect = [
            Exception("First attempt failed"),
            "test-vm-01"
        ]
        mock_vmware_service_class.return_value = mock_vmware_service

        # 模拟工作流重试机制
        mock_execute_activity.side_effect = [
            Exception("First activity attempt failed"),
            "test-vm-01"
        ]

        # 测试活动重试
        with pytest.raises(Exception):
            await create_vm_activity(sample_vm_request)

        # 第二次调用应该成功
        result = await create_vm_activity(sample_vm_request)
        assert result == "test-vm-01"

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_integration_data_flow(self, mock_execute_activity, mock_vmware_service_class):
        """测试集成数据流"""
        # 创建复杂的VM请求
        complex_request = VMRequest(
            vm_name="integration-test-vm",
            guest_id="ubuntu64Guest",
            num_cpus=4,
            memory_gb=8,
            disk_size_gb=100,
            power_on=True,
            notes="Integration test VM"
        )

        # 模拟VMwareService
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.return_value = "integration-test-vm"
        mock_vmware_service_class.return_value = mock_vmware_service

        # 模拟工作流执行
        mock_execute_activity.return_value = "integration-test-vm"

        # 执行工作流
        workflow = VMCreationWorkflow()
        workflow_result = await workflow.run(complex_request)

        # 执行活动
        activity_result = await create_vm_activity(complex_request)

        # 验证数据流
        assert workflow_result == activity_result == "integration-test-vm"

        # 验证请求数据正确传递
        mock_vmware_service.create_vm.assert_called_with(complex_request)

        # 验证请求数据完整性
        call_args = mock_vmware_service.create_vm.call_args[0][0]
        assert call_args.vm_name == "integration-test-vm"
        assert call_args.guest_id == "ubuntu64Guest"
        assert call_args.num_cpus == 4
        assert call_args.memory_gb == 8
        assert call_args.disk_size_gb == 100
        assert call_args.power_on is True
        assert call_args.notes == "Integration test VM"

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_integration_concurrent_executions(self, mock_execute_activity, mock_vmware_service_class):
        """测试集成并发执行"""
        # 创建多个请求
        requests = [
            VMRequest(vm_name=f"concurrent-vm-{i}", num_cpus=2, memory_gb=4, disk_size_gb=40)
            for i in range(3)
        ]

        # 模拟VMwareService
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.side_effect = [req.vm_name for req in requests]
        mock_vmware_service_class.return_value = mock_vmware_service

        # 模拟工作流执行
        mock_execute_activity.side_effect = [req.vm_name for req in requests]

        # 并发执行工作流
        workflow = VMCreationWorkflow()
        workflow_tasks = [workflow.run(req) for req in requests]
        workflow_results = await asyncio.gather(*workflow_tasks)

        # 并发执行活动
        activity_tasks = [create_vm_activity(req) for req in requests]
        activity_results = await asyncio.gather(*activity_tasks)

        # 验证结果
        expected_results = [req.vm_name for req in requests]
        assert workflow_results == activity_results == expected_results

        # 验证所有请求都被处理
        assert mock_vmware_service.create_vm.call_count == 3

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_integration_timeout_handling(self, mock_execute_activity, mock_vmware_service_class, sample_vm_request):
        """测试集成超时处理"""
        # 模拟VMwareService超时
        mock_vmware_service = Mock()
        mock_vmware_service.create_vm.side_effect = Exception("Operation timed out")
        mock_vmware_service_class.return_value = mock_vmware_service

        # 模拟工作流超时
        mock_execute_activity.side_effect = Exception("Activity timed out")

        # 测试活动超时
        with pytest.raises(Exception) as exc_info:
            await create_vm_activity(sample_vm_request)
        assert "创建虚拟机失败: Operation timed out" in str(exc_info.value)

        # 测试工作流超时
        workflow = VMCreationWorkflow()
        with pytest.raises(Exception) as exc_info:
            await workflow.run(sample_vm_request)
        assert "Activity timed out" in str(exc_info.value)

    @patch('temporal_python.activities.vm_activities.VMwareService')
    @patch('temporal_python.workflows.vm_workflows.workflow.execute_activity')
    async def test_integration_resource_validation(self, mock_execute_activity, mock_vmware_service_class):
        """测试集成资源验证"""
        # 测试边界值
        boundary_requests = [
            VMRequest(vm_name="min-vm", num_cpus=1, memory_gb=1, disk_size_gb=1),
            VMRequest(vm_name="max-vm", num_cpus=64, memory_gb=512, disk_size_gb=1024),
        ]

        for request in boundary_requests:
            # 模拟VMwareService
            mock_vmware_service = Mock()
            mock_vmware_service.create_vm.return_value = request.vm_name
            mock_vmware_service_class.return_value = mock_vmware_service

            # 模拟工作流执行
            mock_execute_activity.return_value = request.vm_name

            # 执行工作流和活动
            workflow = VMCreationWorkflow()
            workflow_result = await workflow.run(request)
            activity_result = await create_vm_activity(request)

            # 验证结果
            assert workflow_result == activity_result == request.vm_name
            mock_vmware_service.create_vm.assert_called_with(request)