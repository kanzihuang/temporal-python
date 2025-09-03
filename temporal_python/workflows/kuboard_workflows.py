from datetime import timedelta
from dataclasses import dataclass
from temporalio import workflow
from temporal_python.activities.kuboard_activities import create_namespace_activity, grant_permission_activity

@dataclass
class KuboardNamespaceAuthorizeParams:
    cluster_id: str
    namespace: str
    username: str
    role: str

@dataclass
class KuboardNamespaceCreateParams:
    cluster_id: str
    namespace: str
    username: str
    role: str

@workflow.defn
class KuboardNamespaceAuthorize:
    @workflow.run
    async def run(self, params: KuboardNamespaceAuthorizeParams):
        # 仅授权，要求命名空间已存在
        await workflow.execute_activity(
            grant_permission_activity,
            params.cluster_id,
            params.namespace,
            params.username,
            params.role,
            schedule_to_close_timeout=timedelta(seconds=30),
        )

@workflow.defn
class KuboardNamespaceCreate:
    @workflow.run
    async def run(self, params: KuboardNamespaceCreateParams):
        # 1. 创建命名空间（如果已存在则报错）
        await workflow.execute_activity(
            create_namespace_activity,
            params.cluster_id,
            params.namespace,
            schedule_to_close_timeout=timedelta(seconds=30),
        )
        # 2. 授权
        await workflow.execute_activity(
            grant_permission_activity,
            params.cluster_id,
            params.namespace,
            params.username,
            params.role,
            schedule_to_close_timeout=timedelta(seconds=30),
        )
