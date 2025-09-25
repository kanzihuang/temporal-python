import pytest
import asyncio
from src.activities import kuboard_activities
from src.activities.kuboard_activities import CreateNamespaceParams, GrantPermissionParams

@pytest.mark.asyncio
async def test_create_namespace_activity(monkeypatch):
    called = {}
    class FakeService:
        def create_namespace(self, cluster_id, namespace):
            called['args'] = (cluster_id, namespace)
            return True
    monkeypatch.setattr(kuboard_activities, 'KuBoardService', lambda **kwargs: FakeService())
    monkeypatch.setattr(kuboard_activities, 'ConfigLoader', type('MockConfigLoader', (), {
        'get_kuboard_site_by_cluster': lambda cluster_id: type('MockSite', (), {
            'url': 'http://test.com',
            'username': 'admin',
            'access_key': 'test-access-key',
            'secret_key': 'test-secret-key'
        })()
    }))
    params = CreateNamespaceParams(cluster_id='c1', namespace='ns1')
    result = await kuboard_activities.create_namespace_activity(params)
    assert result is True
    assert called['args'] == ('c1', 'ns1')

@pytest.mark.asyncio
async def test_grant_permission_activity(monkeypatch):
    called = {}
    class FakeService:
        def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
            called['args'] = (cluster_id, namespace, ldap_user_name, role)
            return True
    monkeypatch.setattr(kuboard_activities, 'KuBoardService', lambda **kwargs: FakeService())
    monkeypatch.setattr(kuboard_activities, 'ConfigLoader', type('MockConfigLoader', (), {
        'get_kuboard_site_by_cluster': lambda cluster_id: type('MockSite', (), {
            'url': 'http://test.com',
            'username': 'admin',
            'access_key': 'test-access-key',
            'secret_key': 'test-secret-key'
        })()
    }))
    params = GrantPermissionParams(
        cluster_id='c1',
        namespace='ns1',
        ldap_user_name='user',
        role='admin'
    )
    result = await kuboard_activities.grant_permission_activity(params)
    assert result is True
    assert called['args'] == ('c1', 'ns1', 'user', 'admin')



