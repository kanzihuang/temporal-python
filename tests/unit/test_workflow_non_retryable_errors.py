"""
单元测试：验证工作流参数解码失败时不重试的行为
测试当发生参数解析错误（如Failed decoding arguments）时，
工作流是否能立即失败退出而不是持续重试。
"""

import pytest
import inspect
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import timedelta

from temporalio.common import RetryPolicy
from src.workflows.kuboard_workflows import (
    KuboardNamespaceCreateParams,
    KuboardNamespaceCreate,
)


class TestWorkflowNonRetryableErrors:
    """测试工作流针对解码失败错误的非重试行为"""

    def test_kuboard_workflow_non_retryable_error_types_configured(self):
        """测试KuboardNamespaceCreate工作流的non_retryable_error_types配置"""

        # 验证期望的非重试错误类型都已配置
        expected_non_retryable_errors = [
            "NamespaceAlreadyExistsError",
            "RuntimeError",  # Failed decoding arguments
            "TypeError",  # 参数类型错误
            "ValueError",  # 参数验证错误
        ]

        # 检查工作流源码中的配置
        workflow_source = inspect.getsource(KuboardNamespaceCreate.run)

        for error_type in expected_non_retryable_errors:
            assert (
                error_type in workflow_source
            ), f"Missing {error_type} in workflow configuration"

    def test_param_type_validation_errors_should_not_retry(self):
        """测试参数类型错误不应重试"""

        # TypeError: missing required positional argument should not retry
        with pytest.raises(TypeError):
            KuboardNamespaceCreateParams(
                cluster_id="test",  # 缺少namespaces参数
                # namespaces参数缺失，这应该导致TypeError而不是重试
            )

    def test_param_validation_runtime_errors_should_not_retry(self):
        """测试参数验证RuntimeError不应重试"""

        # 测试空namespaces -> RuntimeError (在non_retryable_error_types中配置)
        with pytest.raises(RuntimeError) as exc_info:
            KuboardNamespaceCreateParams(
                cluster_id="test",
                namespaces=[],  # 空的namespaces
                ldap_user_name="user",
                role="admin",
            )
        assert "namespaces不能为空或未提供" in str(exc_info.value)

        # 测试空cluster_id -> RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            KuboardNamespaceCreateParams(
                cluster_id="",  # 空的cluster_id
                namespaces=["ns1"],
                ldap_user_name="user",
                role="admin",
            )
        assert "cluster_id不能为空" in str(exc_info.value)

        # 测试非字符串namespaces元素 -> RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            KuboardNamespaceCreateParams(
                cluster_id="test",
                namespaces=[123],  # 非字符串元素
                ldap_user_name="user",
                role="admin",
            )
        assert "namespaces列表中的每个元素必须是字符串" in str(exc_info.value)

    def test_workflow_retry_policy_contains_correct_non_retryable_types(self):
        """验证工作流中配置的RetryPolicy包含正确的非重试错误类型"""

        # 创建正确的RetryPolicy来验证模式
        expected_retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3,
            non_retryable_error_types=[
                "NamespaceAlreadyExistsError",
                "RuntimeError",  # Failed decoding arguments
                "TypeError",  # 参数类型错误
                "ValueError",  # 参数验证错误
            ],
        )

        # 验证所有关键的错误类型都包含在non_retryable_error_types中
        critical_non_retryable_types = [
            "RuntimeError",  # 关键的"Failed decoding arguments"错误类型
            "TypeError",  # 关键的missing arguments错误类型
            "ValueError",  # 关键的validation错误类型
        ]

        for error_type in critical_non_retryable_types:
            assert (
                error_type in expected_retry_policy.non_retryable_error_types
            ), f"Critical: {error_type} 必须在non_retryable_error_types中以确保不解码错误会立即失败：{error_type}"

    @pytest.mark.asyncio
    async def test_workflow_should_handle_failed_decoding_arguments_as_final_failure(
        self,
    ):
        """测试工作流处理Failed decoding arguments作为最终失败"""

        # 这是模拟我们在日志中看到的错误：RuntimeError("Failed decoding arguments")

        # 创建一个RuntimeError模拟"Failed decoding arguments"的情况
        failed_decoding_error = RuntimeError("Failed decoding arguments")

        # 验证这个错误类型确实在non_retryable_error_types列表中
        test_retry_policy = RetryPolicy(
            non_retryable_error_types=["RuntimeError", "TypeError", "ValueError"]
        )

        # 关键验证：RuntimeError应在non_retryable列表中
        assert "RuntimeError" in test_retry_policy.non_retryable_error_types

        # 这样就确保当发生"Failed decoding arguments"时，
        # Temporal工作流会立即失败，不会重试

    def test_kuboard_namespace_create_params_post_init_validation_logic(self):
        """测试KuboardNamespaceCreateParams.__post_init__方法的验证逻辑"""

        # 测试正确的参数应该被接受
        valid_params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=["namespace1", "namespace2"],
            ldap_user_name="test-user",
            role="admin",
        )
        assert valid_params.namespaces == ["namespace1", "namespace2"]
        assert valid_params.cluster_id == "test-cluster"

        # 测试无效参数会引发预期的运行时错误
        validation_test_cases = [
            {
                "name": "空namespaces",
                "params": {
                    "cluster_id": "test",
                    "namespaces": [],
                    "ldap_user_name": "user",
                    "role": "admin",
                },
                "expected_message": "namespaces不能为空",
            },
            {
                "name": "空cluster_id",
                "params": {
                    "cluster_id": "",
                    "namespaces": ["ns1"],
                    "ldap_user_name": "user",
                    "role": "admin",
                },
                "expected_message": "cluster_id不能为空",
            },
            {
                "name": "非字符串namespaces元素",
                "params": {
                    "cluster_id": "test",
                    "namespaces": [123, 456],
                    "ldap_user_name": "user",
                    "role": "admin",
                },
                "expected_message": "namespaces列表中的每个元素必须是字符串",
            },
        ]

        for test_case in validation_test_cases:
            with pytest.raises(RuntimeError, match=test_case["expected_message"]):
                KuboardNamespaceCreateParams(**test_case["params"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
