import pytest
from temporal_python.workflows.kuboard_workflows import (
    KuboardNamespaceAuthorize, GrantPermissionParams,
    KuboardNamespaceCreate, KuboardNamespaceCreateParams
)

def test_kuboard_namespace_authorize_params():
    """测试 KuboardNamespaceAuthorize 参数"""
    params = GrantPermissionParams('site1', 'c1', 'ns1', 'user', 'admin')
    assert params.kuboard_site_name == 'site1'
    assert params.cluster_id == 'c1'
    assert params.namespace == 'ns1'
    assert params.ldap_user_name == 'user'
    assert params.role == 'admin'

def test_kuboard_namespace_create_params():
    """测试 KuboardNamespaceCreate 参数"""
    params = KuboardNamespaceCreateParams('site1', 'c1', 'ns1', 'user', 'admin')
    assert params.kuboard_site_name == 'site1'
    assert params.cluster_id == 'c1'
    assert params.namespace == 'ns1'
    assert params.ldap_user_name == 'user'
    assert params.role == 'admin'

def test_workflow_class_definitions():
    """测试工作流类定义"""
    # 验证工作流类存在且可实例化
    auth_workflow = KuboardNamespaceAuthorize()
    create_workflow = KuboardNamespaceCreate()

    assert auth_workflow is not None
    assert create_workflow is not None

    # 验证工作流类有 run 方法
    assert hasattr(auth_workflow, 'run')
    assert hasattr(create_workflow, 'run')

def test_workflow_parameters_validation():
    """测试工作流参数验证"""
    # 测试有效参数
    valid_params = GrantPermissionParams('site1', 'cluster1', 'namespace1', 'user1', 'admin')
    assert valid_params.kuboard_site_name == 'site1'
    assert valid_params.cluster_id == 'cluster1'
    assert valid_params.namespace == 'namespace1'
    assert valid_params.ldap_user_name == 'user1'
    assert valid_params.role == 'admin'

    # 测试不同角色
    edit_params = GrantPermissionParams('site1', 'cluster1', 'namespace1', 'user1', 'edit')
    assert edit_params.role == 'edit'

    view_params = GrantPermissionParams('site1', 'cluster1', 'namespace1', 'user1', 'view')
    assert view_params.role == 'view'
