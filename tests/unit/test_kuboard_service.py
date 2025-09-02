import pytest
from temporal_python.services.kuboard_service import KuBoardService

def test_create_namespace(monkeypatch):
    service = KuBoardService()
    called = {}
    def fake_create_namespace(cluster_id, namespace):
        called['args'] = (cluster_id, namespace)
        return True
    monkeypatch.setattr(service, 'create_namespace', fake_create_namespace)
    assert service.create_namespace('c1', 'ns1') is True
    assert called['args'] == ('c1', 'ns1')

def test_grant_permission(monkeypatch):
    service = KuBoardService()
    called = {}
    def fake_grant_permission(cluster_id, namespace, username, role):
        called['args'] = (cluster_id, namespace, username, role)
        return True
    monkeypatch.setattr(service, 'grant_permission', fake_grant_permission)
    assert service.grant_permission('c1', 'ns1', 'user', 'admin') is True
    assert called['args'] == ('c1', 'ns1', 'user', 'admin')



