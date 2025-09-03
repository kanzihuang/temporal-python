import asyncio
from temporalio.worker import Worker
from temporal_python.workflows.kuboard_workflows import KuboardNamespaceAuthorize, KuboardNamespaceCreate
from temporal_python.activities.kuboard_activities import create_namespace_activity, grant_permission_activity
from temporal_python.shared.config import get_temporal_client

async def main():
    client = await get_temporal_client()
    worker = Worker(
        client,
        task_queue="kuboard",
        workflows=[KuboardNamespaceAuthorize, KuboardNamespaceCreate],
        activities=[create_namespace_activity, grant_permission_activity],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
