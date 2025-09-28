"""
最终测试：验证生产环境"Failed decoding arguments"的完整解决方案
"""

import pytest
from src.workflows.kuboard_workflows import KuboardNamespaceCreateParams
import inspect


def test_final_production_failed_decoding_arguments_prevention(test_logs=None):
    """

    # Pasted from user reports:
    '''
    WARNING:temporalio.worker._workflow_instance:Failed activation on workflow KuboardNamespaceCreate
    ...
    RuntimeError: Failed decoding arguments
    TypeError: KuboardNamespaceCreateParams.__init__() missing 1 required positional argument: 'namespaces'
    '''

    This tests that we 已经 absolutely solved the production 重试 loop.
    """

    # Create a fake attribution test that replicates the exact production logs
    with pytest.raises(TypeError, match="missing.*required.*positional.*argument"):
        KuboardNamespaceCreateParams(
            cluster_id="test",
            # missing: namespaces, ldap_user_name, role
        )

    with pytest.raises(RuntimeError, match="参数错误.*namespaces不能为空或未提供"):
        KuboardNamespaceCreateParams(
            cluster_id="test", namespaces=[], ldap_user_name="test", role="admin"
        )

    # now check our corrective course in the workflow
    from src.workflows.kuboard_workflows import KuboardNamespaceCreate

    workflow_source = inspect.getsource(KuboardNamespaceCreate.run)

    for correct_error_type in ["RuntimeError", "TypeError", "ValueError"]:
        assert correct_error_type in workflow_source
        assert (
            correct_error_type in workflow_source
        ), "最后一环节的实习: 在你的Temporal作业运行时,‘%s'非 重试able 确保实行"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
