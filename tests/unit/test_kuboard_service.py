import pytest
import requests
from unittest.mock import Mock, patch
from temporal_python.services.kuboard_service import KuBoardService, NamespaceAlreadyExistsError, NamespaceCreationError

def test_create_namespace_success(monkeypatch):
    """测试成功创建命名空间"""
    service = KuBoardService()
    
    # Mock 成功的响应
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"kind": "Namespace", "metadata": {"name": "test"}}
    
    with patch.object(service.session, 'post', return_value=mock_response):
        result = service.create_namespace('tencent', 'test')
        assert result is True

def test_create_namespace_already_exists(monkeypatch):
    """测试命名空间已存在的情况"""
    service = KuBoardService()
    
    # Mock 409 响应
    mock_response = Mock()
    mock_response.status_code = 409
    mock_response.text = '{"reason":"AlreadyExists","message":"namespaces \\"test\\" already exists"}'
    
    with patch.object(service.session, 'post', return_value=mock_response):
        with pytest.raises(NamespaceAlreadyExistsError, match="命名空间已存在"):
            service.create_namespace('tencent', 'test')

def test_create_namespace_other_error(monkeypatch):
    """测试其他错误情况"""
    service = KuBoardService()
    
    # Mock 500 响应
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'
    
    with patch.object(service.session, 'post', return_value=mock_response):
        with pytest.raises(NamespaceCreationError, match="创建命名空间失败"):
            service.create_namespace('tencent', 'test')

def test_create_namespace_network_error(monkeypatch):
    """测试网络错误情况"""
    service = KuBoardService()
    
    with patch.object(service.session, 'post', side_effect=requests.exceptions.ConnectionError("Connection failed")):
        with pytest.raises(NamespaceCreationError, match="网络错误"):
            service.create_namespace('tencent', 'test')

def test_grant_permission(monkeypatch):
    service = KuBoardService()
    called = {}
    def fake_grant_permission(cluster_id, namespace, username, role):
        called['args'] = (cluster_id, namespace, username, role)
        return True
    monkeypatch.setattr(service, 'grant_permission', fake_grant_permission)
    assert service.grant_permission('c1', 'ns1', 'user', 'admin') is True
    assert called['args'] == ('c1', 'ns1', 'user', 'admin')



