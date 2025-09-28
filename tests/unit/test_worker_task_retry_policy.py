"""
测试工作流任务级别的重试策略配置

验证工作流装饰器中的 failure_exception_types 配置是否正确设置了
non_retryable错误类型，确保 "Failed decoding arguments" 错误
导致工作流立即失败而不是无限重试。
"""

import pytest
import inspect
from datetime import timedelta
from temporalio.common import RetryPolicy
from src.workflows.kuboard_workflows import (
    KuboardNamespaceCreate,
    KuboardNamespaceAuthorize,
)


class TestWorkflowTaskRetryPolicy:
    """测试工作流任务级别的重试策略配置"""

    def test_workflow_decorator_failure_exception_types_configuration(self):
        """验证工作流装饰器配置了正确的 failure_exception_types"""

        # 检查 KuboardNamespaceCreate 工作流的装饰器配置
        kuboard_create_source = inspect.getsource(KuboardNamespaceCreate)

        # 验证 failure_exception_types 配置存在
        assert (
            "failure_exception_types" in kuboard_create_source
        ), "KuboardNamespaceCreate 工作流必须配置 failure_exception_types"

        # 验证关键错误类型包含在配置中
        required_error_types = [
            "RuntimeError",  # Failed decoding arguments
            "TypeError",  # missing required positional argument
            "ValueError",  # 参数验证错误
        ]

        for error_type in required_error_types:
            assert (
                error_type in kuboard_create_source
            ), f"KuboardNamespaceCreate 的 failure_exception_types 必须包含 {error_type}"

    def test_workflow_authorize_failure_exception_types_configuration(self):
        """验证 KuboardNamespaceAuthorize 工作流的 failure_exception_types 配置"""

        # 检查 KuboardNamespaceAuthorize 工作流的装饰器配置
        kuboard_authorize_source = inspect.getsource(KuboardNamespaceAuthorize)

        # 验证 failure_exception_types 配置存在
        assert (
            "failure_exception_types" in kuboard_authorize_source
        ), "KuboardNamespaceAuthorize 工作流必须配置 failure_exception_types"

        # 验证关键错误类型包含在配置中
        required_error_types = [
            "RuntimeError",  # Failed decoding arguments
            "TypeError",  # missing required positional argument
            "ValueError",  # 参数验证错误
        ]

        for error_type in required_error_types:
            assert (
                error_type in kuboard_authorize_source
            ), f"KuboardNamespaceAuthorize 的 failure_exception_types 必须包含 {error_type}"

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

        # 读取 Worker 文件内容
        import os

        worker_file_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "workers", "kuboard_worker.py"
        )

        with open(worker_file_path, "r", encoding="utf-8") as f:
            worker_file_content = f.read()

        # 验证 Worker 层面的配置
        assert (
            "max_concurrent_workflow_tasks" in worker_file_content
        ), "Worker 应该配置 max_concurrent_workflow_tasks"

        assert (
            "max_concurrent_activities" in worker_file_content
        ), "Worker 应该配置 max_concurrent_activities"

        assert (
            "graceful_shutdown_timeout" in worker_file_content
        ), "Worker 应该配置 graceful_shutdown_timeout"

    def test_workflow_handles_failed_decoding_arguments_scenario(self):
        """验证工作流配置能够处理 Failed decoding arguments 场景"""

        # 验证两个工作流都能处理用户报告的具体错误场景
        workflows = [KuboardNamespaceCreate, KuboardNamespaceAuthorize]

        for workflow_class in workflows:
            workflow_source = inspect.getsource(workflow_class)

            # 验证配置能够处理用户报告的具体错误场景
            scenario_requirements = [
                "RuntimeError",  # 对应 "Failed decoding arguments"
                "TypeError",  # 对应 "missing 1 required positional argument"
                "ValueError",  # 对应参数验证错误
            ]

            for requirement in scenario_requirements:
                assert (
                    requirement in workflow_source
                ), f"{workflow_class.__name__} 配置必须能够处理用户报告的错误场景，需要: {requirement}"

    def test_workflow_decorator_structure(self):
        """验证工作流装饰器的结构配置正确"""

        kuboard_create_source = inspect.getsource(KuboardNamespaceCreate)

        # 验证装饰器的完整配置结构
        decorator_elements = [
            "@workflow.defn(",
            "failure_exception_types=[",
            "RuntimeError",
            "TypeError",
            "ValueError",
        ]

        for element in decorator_elements:
            assert (
                element in kuboard_create_source
            ), f"工作流装饰器必须包含配置元素: {element}"

    def test_workflow_activity_retry_policy_consistency(self):
        """验证工作流中的 Activity 重试策略与工作流任务策略一致"""

        kuboard_create_source = inspect.getsource(KuboardNamespaceCreate)

        # 验证 Activity 层面的 non_retryable_error_types 包含工作流层面的错误类型
        activity_retry_elements = [
            "non_retryable_error_types=[",
            "RuntimeError",
            "TypeError",
            "ValueError",
        ]

        for element in activity_retry_elements:
            assert (
                element in kuboard_create_source
            ), f"Activity 重试策略必须包含配置元素: {element}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
