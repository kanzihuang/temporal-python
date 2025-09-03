import pytest
import asyncio
from temporal_python.activities import kuboard_activities

@pytest.mark.asyncio
async def test_create_namespace_activity(monkeypatch):
    called = {}
    class FakeService:
        def create_namespace(self, cluster_id, namespace):
            called['args'] = (cluster_id, namespace)
            return True
    monkeypatch.setattr(kuboard_activities, 'KuBoardService', lambda **kwargs: FakeService())
    monkeypatch.setattr(kuboard_activities, 'ConfigLoader', type('MockConfigLoader', (), {
        'get_kuboard_site': lambda site_name: type('MockSite', (), {
            'url': 'http://test.com',
            'username': 'admin',
            'access_key': 'test-access-key',
            'secret_key': 'test-secret-key'
        })()
    }))
    result = await kuboard_activities.create_namespace_activity('site1', 'c1', 'ns1')
    assert result is True
    assert called['args'] == ('c1', 'ns1')

@pytest.mark.asyncio
async def test_grant_permission_activity(monkeypatch):
    called = {}
    class FakeService:
        def grant_permission(self, cluster_id, namespace, username, role):
            called['args'] = (cluster_id, namespace, username, role)
            return True
    monkeypatch.setattr(kuboard_activities, 'KuBoardService', lambda **kwargs: FakeService())
    monkeypatch.setattr(kuboard_activities, 'ConfigLoader', type('MockConfigLoader', (), {
        'get_kuboard_site': lambda site_name: type('MockSite', (), {
            'url': 'http://test.com',
            'username': 'admin',
            'access_key': 'test-access-key',
            'secret_key': 'test-secret-key'
        })()
    }))
    result = await kuboard_activities.grant_permission_activity('site1', 'c1', 'ns1', 'user', 'admin')
    assert result is True
    assert called['args'] == ('c1', 'ns1', 'user', 'admin')



