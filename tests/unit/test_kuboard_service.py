import pytest
import requests
from unittest.mock import Mock, patch
from temporal_python.services.kuboard_service import (
    KuBoardService,
    NamespaceAlreadyExistsError,
    NamespaceCreationError,
    NamespaceNotFoundError,
    KuboardAuthError,
    KuboardNetworkError
)

def test_create_namespace_success(monkeypatch):
    """测试成功创建命名空间"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 成功的响应
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"kind": "Namespace", "metadata": {"name": "test"}}

    with patch.object(service.session, 'post', return_value=mock_response):
        result = service.create_namespace('tencent', 'test')
        assert result is True

def test_create_namespace_already_exists(monkeypatch):
    """测试命名空间已存在的情况"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 409 响应
    mock_response = Mock()
    mock_response.status_code = 409
    mock_response.text = '{"reason":"AlreadyExists","message":"namespaces \\"test\\" already exists"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        with pytest.raises(NamespaceAlreadyExistsError, match="命名空间已存在"):
            service.create_namespace('tencent', 'test')

def test_create_namespace_other_error(monkeypatch):
    """测试其他错误情况"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 500 响应
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'

    with patch.object(service.session, 'post', return_value=mock_response):
        with pytest.raises(NamespaceCreationError, match="创建命名空间失败"):
            service.create_namespace('tencent', 'test')

def test_create_namespace_network_error(monkeypatch):
    """测试网络错误情况"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    with patch.object(service.session, 'post', side_effect=requests.exceptions.ConnectionError("Connection failed")):
        with pytest.raises(NamespaceCreationError, match="网络错误"):
            service.create_namespace('tencent', 'test')

def test_grant_permission(monkeypatch):
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 两个阶段的授权方法
    def mock_stage1(cluster_id, username):
        return None  # 成功时不抛出异常

    def mock_stage2(cluster_id, namespace, username, role):
        return None  # 成功时不抛出异常

    monkeypatch.setattr(service, '_grant_stage1_permission', mock_stage1)
    monkeypatch.setattr(service, '_grant_stage2_permission', mock_stage2)

    result = service.grant_permission('c1', 'ns1', 'user', 'admin')
    assert result is True

def test_grant_stage1_permission_success(monkeypatch):
    """测试第一阶段授权成功"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 成功的响应
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"status":"success"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        # 应该不抛出异常
        service._grant_stage1_permission('tencent', 'test')

def test_grant_stage1_permission_already_exists(monkeypatch):
    """测试第一阶段授权已存在"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 已存在的响应
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = '{"error":"对象已存在"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        # 应该不抛出异常
        service._grant_stage1_permission('tencent', 'test')

def test_grant_stage1_permission_error(monkeypatch):
    """测试第一阶段授权失败"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 失败的响应
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = '{"error":"Bad Request"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        with pytest.raises(KuboardAuthError, match="第一阶段授权失败"):
            service._grant_stage1_permission('tencent', 'test')

def test_grant_stage2_permission_success(monkeypatch):
    """测试第二阶段授权成功"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 成功的响应
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.text = '{"status":"success"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        # 应该不抛出异常
        service._grant_stage2_permission('tencent', 'test', 'user', 'edit')

def test_grant_stage2_permission_already_exists(monkeypatch):
    """测试第二阶段授权已存在"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 已存在的响应
    mock_response = Mock()
    mock_response.status_code = 409
    mock_response.text = '{"error":"already exists"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        # 应该不抛出异常
        service._grant_stage2_permission('tencent', 'test', 'user', 'edit')

def test_grant_stage2_permission_error(monkeypatch):
    """测试第二阶段授权失败"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 失败的响应
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = '{"error":"Bad Request"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        with pytest.raises(KuboardAuthError, match="第二阶段授权失败"):
            service._grant_stage2_permission('tencent', 'test', 'user', 'edit')


def test_grant_stage2_permission_namespace_not_found(monkeypatch):
    """测试第二阶段授权时命名空间不存在"""
    service = KuBoardService(
        base_url="http://test.com:8089",
        username="admin",
        access_key="test-access-key",
        secret_key="test-secret-key"
    )

    # Mock 404 响应（命名空间不存在）
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = '{"error":"namespace not found"}'

    with patch.object(service.session, 'post', return_value=mock_response):
        with pytest.raises(NamespaceNotFoundError, match="命名空间不存在"):
            service._grant_stage2_permission('tencent', 'nonexistent', 'user', 'edit')



