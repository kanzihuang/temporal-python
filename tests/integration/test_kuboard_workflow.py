import pytest
import asyncio
from temporalio.testing import WorkflowEnvironment
from temporal_python.workflows.kuboard_workflows import KuboardNamespaceAuthorize, KuboardNamespaceAuthorizeParams
from temporal_python.activities import kuboard_activities

@pytest.mark.asyncio
async def test_kuboard_namespace_authorize(monkeypatch):
    called = {'create': None, 'grant': None}
    async def fake_create_namespace_activity(cluster_id, namespace):
        called['create'] = (cluster_id, namespace)
        return True
    async def fake_grant_permission_activity(cluster_id, namespace, username, role):
        called['grant'] = (cluster_id, namespace, username, role)
        return True
    monkeypatch.setattr(kuboard_activities, 'create_namespace_activity', fake_create_namespace_activity)
    monkeypatch.setattr(kuboard_activities, 'grant_permission_activity', fake_grant_permission_activity)

    async with await WorkflowEnvironment.start_local() as env:
        handle = await env.client.start_workflow(
            KuboardNamespaceAuthorize.run,
            KuboardNamespaceAuthorizeParams('c1', 'ns1', 'user', 'admin'),
            id="test-kuboard-ns-auth",
            task_queue="kuboard",
        )
        await handle.result()
        assert called['create'] == ('c1', 'ns1')
        assert called['grant'] == ('c1', 'ns1', 'user', 'admin')
