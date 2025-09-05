import pytest
import asyncio
from temporal_python.activities import kuboard_activities
from temporal_python.activities.kuboard_activities import CreateNamespaceParams, GrantPermissionParams

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
    params = CreateNamespaceParams(kuboard_site_name='site1', cluster_id='c1', namespace='ns1')
    result = await kuboard_activities.create_namespace_activity(params)
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
    params = GrantPermissionParams(
        kuboard_site_name='site1',
        cluster_id='c1',
        namespace='ns1',
        username='user',
        role='admin'
    )
    result = await kuboard_activities.grant_permission_activity(params)
    assert result is True
    assert called['args'] == ('c1', 'ns1', 'user', 'admin')



