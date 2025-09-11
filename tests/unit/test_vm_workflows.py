"""
Unit tests for src.workflows.vm_workflows module.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, ANY
from datetime import timedelta
from src.workflows.vm_workflows import VMCreationWorkflow
from src.shared.schemas import VMRequest


class TestVMCreationWorkflow:
    """Test VM creation workflow."""

    @patch('src.workflows.vm_workflows.workflow.execute_activity', new_callable=AsyncMock)
    async def test_run_success(self, mock_execute_activity, sample_vm_request):
        """测试工作流成功执行"""
        # 模拟活动执行成功
        mock_execute_activity.return_value = "test-vm-01"

        # 创建工作流实例
        workflow = VMCreationWorkflow()

        # 执行工作流
        result = await workflow.run(sample_vm_request)

        # 验证结果
        assert result == "test-vm-01"

        # 验证execute_activity被正确调用
        mock_execute_activity.assert_called_once()
        called_args = mock_execute_activity.call_args
        assert called_args[0][0] == "create_vm_activity"
        assert called_args[0][1] == sample_vm_request
        assert called_args[1]["schedule_to_close_timeout"].total_seconds() == 1800
        assert called_args[1]["task_queue"] == "vmware"
        assert hasattr(called_args[1]["retry_policy"], "maximum_attempts")

    @patch('src.workflows.vm_workflows.workflow.execute_activity', new_callable=AsyncMock)
    async def test_run_with_different_vm_requests(self, mock_execute_activity):
        """测试不同VM请求的工作流执行"""
        vm_requests = [
            VMRequest(vm_name="test-vm-01", num_cpus=2, memory_gb=4, disk_size_gb=40),
            VMRequest(vm_name="prod-server", num_cpus=8, memory_gb=16, disk_size_gb=200),
            VMRequest(vm_name="dev-env", num_cpus=1, memory_gb=2, disk_size_gb=20),
        ]

        for i, request in enumerate(vm_requests):
            # 模拟活动执行
            mock_execute_activity.return_value = request.vm_name

            # 创建工作流实例
            workflow = VMCreationWorkflow()

            # 执行工作流
            result = await workflow.run(request)

            # 验证结果
            assert result == request.vm_name
            called_args = mock_execute_activity.call_args
            assert called_args[0][0] == "create_vm_activity"
            assert called_args[0][1] == request
            assert called_args[1]["schedule_to_close_timeout"].total_seconds() == 1800
            assert called_args[1]["task_queue"] == "vmware"
            assert hasattr(called_args[1]["retry_policy"], "maximum_attempts")

    @patch('src.workflows.vm_workflows.workflow.execute_activity')
    async def test_run_activity_failure(self, mock_execute_activity, sample_vm_request):
        """测试活动执行失败"""
        # 模拟活动执行失败
        mock_execute_activity.side_effect = Exception("Activity execution failed")

        # 创建工作流实例
        workflow = VMCreationWorkflow()

        # 执行工作流并验证异常
        with pytest.raises(Exception) as exc_info:
            await workflow.run(sample_vm_request)

        # 验证异常信息
        assert "Activity execution failed" in str(exc_info.value)

    @patch('src.workflows.vm_workflows.workflow.execute_activity')
    async def test_run_with_retry_policy(self, mock_execute_activity, sample_vm_request):
        """测试重试策略配置"""
        mock_execute_activity.return_value = "test-vm-01"

        workflow = VMCreationWorkflow()
        await workflow.run(sample_vm_request)

        # 获取调用参数
        call_args = mock_execute_activity.call_args
        retry_policy = call_args[1]['retry_policy']

        # 验证重试策略配置
        assert retry_policy.initial_interval == timedelta(seconds=10)
        assert retry_policy.maximum_interval == timedelta(seconds=60)
        assert retry_policy.maximum_attempts == 5

    @patch('src.workflows.vm_workflows.workflow.execute_activity')
    async def test_run_timeout_configuration(self, mock_execute_activity, sample_vm_request):
        """测试超时配置"""
        mock_execute_activity.return_value = "test-vm-01"

        workflow = VMCreationWorkflow()
        await workflow.run(sample_vm_request)

        # 获取调用参数
        call_args = mock_execute_activity.call_args
        timeout = call_args[1]['schedule_to_close_timeout']

        # 验证超时配置
        assert timeout == timedelta(minutes=30)

    @patch('src.workflows.vm_workflows.workflow.execute_activity')
    async def test_run_task_queue_configuration(self, mock_execute_activity, sample_vm_request):
        """测试任务队列配置"""
        mock_execute_activity.return_value = "test-vm-01"

        workflow = VMCreationWorkflow()
        await workflow.run(sample_vm_request)

        # 获取调用参数
        call_args = mock_execute_activity.call_args
        task_queue = call_args[1]['task_queue']

        # 验证任务队列配置
        assert task_queue == "vmware"

    @patch('src.workflows.vm_workflows.workflow.execute_activity', new_callable=AsyncMock)
    async def test_run_with_complex_vm_request(self, mock_execute_activity):
        """测试复杂VM请求的工作流执行"""
        complex_request = VMRequest(
            vm_name="complex-vm-01",
            guest_id="win2019srv_64Guest",
            num_cpus=16,
            memory_gb=32,
            disk_size_gb=500,
            power_on=False,
            notes="Complex VM with Windows Server 2019"
        )

        mock_execute_activity.return_value = "complex-vm-01"

        workflow = VMCreationWorkflow()
        result = await workflow.run(complex_request)

        # 验证结果
        assert result == "complex-vm-01"
        called_args = mock_execute_activity.call_args
        assert called_args[0][0] == "create_vm_activity"
        assert called_args[0][1] == complex_request
        assert called_args[1]["schedule_to_close_timeout"].total_seconds() == 1800
        assert called_args[1]["task_queue"] == "vmware"
        assert hasattr(called_args[1]["retry_policy"], "maximum_attempts")

    @patch('src.workflows.vm_workflows.workflow.execute_activity')
    async def test_run_activity_returns_different_vm_name(self, mock_execute_activity, sample_vm_request):
        """测试活动返回不同的VM名称"""
        # 模拟活动返回不同的VM名称
        mock_execute_activity.return_value = "different-vm-name"

        workflow = VMCreationWorkflow()
        result = await workflow.run(sample_vm_request)

        # 验证结果
        assert result == "different-vm-name"
        assert result != sample_vm_request.vm_name

    @patch('src.workflows.vm_workflows.workflow.execute_activity')
    async def test_run_multiple_executions(self, mock_execute_activity, sample_vm_request):
        """测试多次执行工作流"""
        mock_execute_activity.return_value = "test-vm-01"

        workflow = VMCreationWorkflow()

        # 多次执行工作流
        results = []
        for i in range(3):
            result = await workflow.run(sample_vm_request)
            results.append(result)

        # 验证所有执行都成功
        assert all(result == "test-vm-01" for result in results)
        assert len(results) == 3

        # 验证活动被调用了3次
        assert mock_execute_activity.call_count == 3

    @patch('src.workflows.vm_workflows.workflow.execute_activity', new_callable=AsyncMock)
    async def test_run_with_minimal_vm_request(self, mock_execute_activity):
        """测试最小VM请求的工作流执行"""
        minimal_request = VMRequest(
            vm_name="minimal-vm",
            num_cpus=1,
            memory_gb=1,
            disk_size_gb=10
        )

        mock_execute_activity.return_value = "minimal-vm"

        workflow = VMCreationWorkflow()
        result = await workflow.run(minimal_request)

        # 验证结果
        assert result == "minimal-vm"
        called_args = mock_execute_activity.call_args
        assert called_args[0][0] == "create_vm_activity"
        assert called_args[0][1] == minimal_request
        assert called_args[1]["schedule_to_close_timeout"].total_seconds() == 1800
        assert called_args[1]["task_queue"] == "vmware"
        assert hasattr(called_args[1]["retry_policy"], "maximum_attempts")

    @patch('src.workflows.vm_workflows.workflow.execute_activity', new_callable=AsyncMock)
    async def test_run_workflow_defn_attributes(self, mock_execute_activity):
        """测试工作流定义属性"""
        # 验证工作流类有正确的装饰器
        assert hasattr(VMCreationWorkflow, '__temporal_workflow_defn__')

        # 验证工作流名称
        workflow_defn = VMCreationWorkflow.__temporal_workflow_defn__
        assert workflow_defn.name == "vm_creation_workflow"

    @patch('src.workflows.vm_workflows.workflow.execute_activity', new_callable=AsyncMock)
    async def test_run_method_attributes(self, mock_execute_activity):
        """测试run方法的属性"""
        # 验证run方法有正确的装饰器
        run_method = VMCreationWorkflow.run
        assert hasattr(run_method, '__temporal_run__')

        # 验证方法签名
        import inspect
        sig = inspect.signature(run_method)
        params = list(sig.parameters.keys())

        # 应该包含self和request参数
        assert 'self' in params
        assert 'request' in params

    def test_workflow_decorator_properties(self):
        """测试工作流装饰器属性"""
        from src.workflows.vm_workflows import create_vm_workflow
        assert callable(create_vm_workflow)
        assert create_vm_workflow.__name__ == "create_vm_workflow"
        import asyncio
        assert asyncio.iscoroutinefunction(create_vm_workflow)