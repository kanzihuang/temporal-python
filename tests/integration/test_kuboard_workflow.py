import pytest
from src.workflows.kuboard_workflows import (
    KuboardNamespaceAuthorize,
    GrantPermissionParams,
    KuboardNamespaceCreate,
    KuboardNamespaceCreateParams,
)


def test_kuboard_namespace_authorize_params():
    """测试 KuboardNamespaceAuthorize 参数"""
    params = GrantPermissionParams("c1", "ns1", "user", "admin")
    assert params.cluster_id == "c1"
    assert params.namespace == "ns1"
    assert params.ldap_user_name == "user"
    assert params.role == "admin"


def test_kuboard_namespace_create_params():
    """测试 KuboardNamespaceCreate 参数"""
    params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2", "ns3"],
        ldap_user_name="user",
        role="admin",
    )
    assert params.cluster_id == "c1"
    assert params.namespaces == ["ns1", "ns2", "ns3"]
    assert params.ldap_user_name == "user"
    assert params.role == "admin"


def test_workflow_class_definitions():
    """测试工作流类定义"""
    # 验证工作流类存在且可实例化
    auth_workflow = KuboardNamespaceAuthorize()
    create_workflow = KuboardNamespaceCreate()

    assert auth_workflow is not None
    assert create_workflow is not None

    # 验证工作流类有 run 方法
    assert hasattr(auth_workflow, "run")
    assert hasattr(create_workflow, "run")


def test_workflow_parameters_validation():
    """测试工作流参数验证"""
    # 测试有效参数
    valid_params = GrantPermissionParams("cluster1", "namespace1", "user1", "admin")
    assert valid_params.cluster_id == "cluster1"
    assert valid_params.namespace == "namespace1"
    assert valid_params.ldap_user_name == "user1"
    assert valid_params.role == "admin"

    # 测试不同角色
    edit_params = GrantPermissionParams("cluster1", "namespace1", "user1", "edit")
    assert edit_params.role == "edit"

    view_params = GrantPermissionParams("cluster1", "namespace1", "user1", "view")
    assert view_params.role == "view"


def test_kuboard_namespace_create_params_multiple_namespaces():
    """测试多个命名空间的参数创建"""
    # 测试空列表
    empty_params = KuboardNamespaceCreateParams(
        cluster_id="c1", namespaces=[], ldap_user_name="user", role="admin"
    )
    assert empty_params.namespaces == []

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
    assert len(multi_params.namespaces) == 4
    assert multi_params.namespaces == ["ns1", "ns2", "ns3", "ns4"]


def test_kuboard_namespace_create_params_different_roles():
    """测试不同角色的参数"""
    # 测试 admin 角色
    admin_params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2"],
        ldap_user_name="admin_user",
        role="admin",
    )
    assert admin_params.role == "admin"

    # 测试 edit 角色
    edit_params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2"],
        ldap_user_name="edit_user",
        role="edit",
    )
    assert edit_params.role == "edit"

    # 测试 viewer 角色
    viewer_params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2"],
        ldap_user_name="viewer_user",
        role="viewer",
    )
    assert viewer_params.role == "viewer"


def test_kuboard_namespace_create_params_different_users():
    """测试不同用户的参数"""
    # 测试不同用户名的参数
    user1_params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2"],
        ldap_user_name="john.doe",
        role="admin",
    )
    assert user1_params.ldap_user_name == "john.doe"

    user2_params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2"],
        ldap_user_name="jane.smith",
        role="edit",
    )
    assert user2_params.ldap_user_name == "jane.smith"
