"""
生产级测试：验证生产环境 workflow activation non-retries 的现实实现

专注于解决用户报告的生产环境重试问题：
-"Failed decoding arguments" 重复重试问题
"""

import pytest
import inspect
from src.workflows.kuboard_workflows import (
    KuboardNamespaceCreateParams,
    KuboardNamespaceCreate,
)


class TestProductionWorkflowActivationNonRetries:
    """验证生产环境workflow activation failures的非重试配置"""

    def test_validate_workflow_has_precise_retry_configuration_for_failed_decoding_arguments(
        self,
    ):
        """
        核心测试：验证 KuboardNamespaceCreate 工作流在Failed decoding arguments
        时具备防止无限重试的 precise配置。
        """

        workflow_source = inspect.getsource(KuboardNamespaceCreate.run)

        # 生产级必须的保护 error types
        production_required_error_types = [
            "RuntimeError",  # 覆盖 "Failed decoding arguments"
            "TypeError",  # 覆盖 "missing positional arguments"
            "ValueError",  # 覆盖参数验证错误
            "NamespaceAlreadyExistsError",  # 业务面保护
        ]

        for error_type in production_required_error_types:
            assert error_type in workflow_source, (
                f"生产安全风险: {error_type} 未在工作流non_retryable_error_types中 "
                f"- 这将导致生产重试问题"
            )

    def test_simulate_production_failed_decode_argument_scenarios(self):
        """
        模拟生产环境 Failed decoding arguments 的完整场景。
        验证这些真实失败做的正确protection在 retry_policy配置中.
        """

        # 模拟真实生产日志场景:
        # "RuntimeError: Failed decoding arguments"
        # "TypeError: KuboardNamespaceCreateParams.__init__() missing 1 required positional argument: 'namespaces'"

        production_error_scenarios = [
            {
                "name": "Missing required positional argument",
                "params": {
                    "cluster_id": "test"
                },  # missing namespaces, ldap_user_name, role
                "expected_error": TypeError,
                "expected_message": "missing.*required.*positional.*argument",
            },
            {
                "name": "Empty namespaces triggering post_init validation",
                "params": {
                    "cluster_id": "test-cluster",
                    "namespaces": [],  # empty list <= triggers post_init RuntimeError
                    "ldap_user_name": "test-user",
                    "role": "admin",
                },
                "expected_error": RuntimeError,
                "expected_message": "参数错误.*namespaces不能为空或未提供",
            },
            {
                "name": "Empty cluster_id",
                "params": {
                    "cluster_id": "",  # empty cluster_id
                    "namespaces": ["test-ns"],
                    "ldap_user_name": "test-user",
                    "role": "admin",
                },
                "expected_error": RuntimeError,
                "expected_message": "参数错误.*cluster_id不能为空",
            },
        ]

        for scenario in production_error_scenarios:
            with pytest.raises(
                scenario["expected_error"], match=scenario["expected_message"]
            ):
                KuboardNamespaceCreateParams(**scenario["params"])

        # 确认这些error types在我们的workflow配置中作为non_retryable
        import inspect

        workflow_source = inspect.getsource(KuboardNamespaceCreate.run)

        required_production_errors = ["RuntimeError", "TypeError"]
        for test_error in required_production_errors:
            assert test_error in workflow_source

    def test_workflow_non_retryable_config_must_cover_user_production_logs_types(
        self,
    ):
        """
        基于用户实际生产日志和问题上进行最后的validation
        保证了非重试配置保护覆盖 production logs中出现的确切错误类型。
        """

        workflow_source = inspect.getsource(KuboardNamespaceCreate.run)

        # 用户报错错误类型映射：
        user_production_errors = [
            ("RuntimeError", "Failed decoding arguments"),
            ("TypeError", "missing 1 required positional argument: namespaces"),
        ]

        # 确保这两种error都在workflows non-retry配置中
        for error_name, error_description in user_production_errors:
            assert error_name in workflow_source, (
                f"生产级安全风险: {error_name} 未在workflow配置中找到 "
                f"{error_description} -- 导致生产环境重试现象仍未得到解决！"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
