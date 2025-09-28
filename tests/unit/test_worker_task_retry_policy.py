"""
测试 Worker 任务级别的重试策略配置

验证 Worker 配置的 workflow_task_retry_policy 是否正确设置了
non_retryable_error_types，确保 "Failed decoding arguments" 错误
导致工作流立即失败而不是无限重试。
"""

import pytest
import inspect
from datetime import timedelta
from temporalio.common import RetryPolicy
from src.workers.kuboard_worker import main


class TestWorkerTaskRetryPolicy:
    """测试 Worker 任务级别的重试策略配置"""

    def test_worker_imports_required_modules(self):
        """验证 Worker 模块导入了必要的依赖"""

        # 读取整个文件内容来检查导入
        import os

        worker_file_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "workers", "kuboard_worker.py"
        )

        with open(worker_file_path, "r", encoding="utf-8") as f:
            worker_file_content = f.read()

        required_imports = [
            "from datetime import timedelta",
            "from temporalio.common import RetryPolicy",
        ]

        for import_statement in required_imports:
            assert (
                import_statement in worker_file_content
            ), f"Worker 必须导入 {import_statement} 来配置工作流任务重试策略"

    def test_worker_workflow_task_retry_policy_configuration(self):
        """验证 Worker 配置了正确的工作流任务重试策略"""

        worker_source = inspect.getsource(main)

        # 验证 workflow_task_retry_policy 配置存在
        assert (
            "workflow_task_retry_policy" in worker_source
        ), "Worker 必须配置 workflow_task_retry_policy 来控制工作流任务重试"

        # 验证 maximum_attempts=1
        assert (
            "maximum_attempts=1" in worker_source
        ), "Worker 必须设置 maximum_attempts=1 确保失败后不重试"

        # 验证 non_retryable_error_types 包含关键错误类型
        required_error_types = [
            "RuntimeError",  # Failed decoding arguments
            "TypeError",  # missing required positional argument
            "ValueError",  # 参数验证错误
        ]

        for error_type in required_error_types:
            assert (
                error_type in worker_source
            ), f"Worker 的 non_retryable_error_types 必须包含 {error_type}"

    def test_worker_workflow_task_timeout_configuration(self):
        """验证 Worker 配置了工作流任务超时"""

        worker_source = inspect.getsource(main)

        # 验证 workflow_task_timeout 配置
        assert (
            "workflow_task_timeout" in worker_source
        ), "Worker 必须配置 workflow_task_timeout"

        assert (
            "timedelta(seconds=60)" in worker_source
        ), "Worker 应该设置合理的任务超时时间（60秒）"

    def test_worker_logging_configuration(self):
        """验证 Worker 配置了适当的日志输出"""

        worker_source = inspect.getsource(main)

        # 验证日志输出包含重试策略信息
        expected_log_messages = [
            "工作流任务配置",
            "任务超时：60秒",
            "最大重试次数：1",
            "非重试错误类型",
        ]

        for log_message in expected_log_messages:
            assert (
                log_message in worker_source
            ), f"Worker 应该输出日志信息: {log_message}"

    def test_worker_retry_policy_structure(self):
        """验证 RetryPolicy 的结构配置正确"""

        worker_source = inspect.getsource(main)

        # 验证 RetryPolicy 的完整配置结构
        retry_policy_elements = [
            "RetryPolicy(",
            "initial_interval=timedelta(seconds=1)",
            "maximum_interval=timedelta(seconds=10)",
            "maximum_attempts=1",
            "non_retryable_error_types=[",
        ]

        for element in retry_policy_elements:
            assert element in worker_source, f"RetryPolicy 必须包含配置元素: {element}"

    def test_worker_handles_failed_decoding_arguments_scenario(self):
        """验证 Worker 配置能够处理 Failed decoding arguments 场景"""

        worker_source = inspect.getsource(main)

        # 验证配置能够处理用户报告的具体错误场景
        scenario_requirements = [
            "RuntimeError",  # 对应 "Failed decoding arguments"
            "TypeError",  # 对应 "missing 1 required positional argument"
            "maximum_attempts=1",  # 确保不重试
        ]

        for requirement in scenario_requirements:
            assert (
                requirement in worker_source
            ), f"Worker 配置必须能够处理用户报告的错误场景，需要: {requirement}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
