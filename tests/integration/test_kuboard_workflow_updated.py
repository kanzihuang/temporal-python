import pytest
from src.workflows.kuboard_workflows import KuboardNamespaceCreateParams


def test_kuboard_namespace_create_params_multiple_namespaces():
    """测试多个命名空间的参数创建"""

    # 修正：空列表测试应该期望出异常，而不是允许它通过
    with pytest.raises(RuntimeError, match="参数错误：namespaces不能为空或未提供"):
        KuboardNamespaceCreateParams(
            cluster_id="c1", namespaces=[], ldap_user_name="user", role="admin"
        )

    # 测试单个命名空间
    single_params = KuboardNamespaceCreateParams(
        cluster_id="c1", namespaces=["ns1"], ldap_user_name="user", role="admin"
    )
    assert single_params.namespaces == ["ns1"]

    # 测试多个命名空间
    multi_params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2", "ns3", "ns4"],
        ldap_user_name="user",
        role="admin",
    )
    assert multi_params.namespaces == ["ns1", "ns2", "ns3", "ns4"]

    # 测试大量命名空间
    bulk_params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["namespace_" + str(i) for i in range(100)],
        ldap_user_name="user",
        role="admin",
    )
    assert len(bulk_params.namespaces) == 100
    assert bulk_params.namespaces[0] == "namespace_0"
