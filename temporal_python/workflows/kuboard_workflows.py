from datetime import timedelta
from dataclasses import dataclass
from temporalio import workflow
from temporal_python.activities.kuboard_activities import create_namespace_activity, grant_permission_activity
from temporal_python.services.kuboard_service import NamespaceAlreadyExistsError

@dataclass
class KuboardNamespaceAuthorizeParams:
    kuboard_site_name: str
    cluster_id: str
    namespace: str
    username: str
    role: str

@dataclass
class KuboardNamespaceCreateParams:
    kuboard_site_name: str
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
            params.kuboard_site_name,
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
        try:
            await workflow.execute_activity(
                create_namespace_activity,
                params.kuboard_site_name,
                params.cluster_id,
                params.namespace,
                schedule_to_close_timeout=timedelta(seconds=30),
                retry_policy=workflow.RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                    non_retryable_error_types=[NamespaceAlreadyExistsError]
                )
            )
        except NamespaceAlreadyExistsError:
            # 命名空间已存在，抛出异常
            raise
        # 2. 授权
        await workflow.execute_activity(
            grant_permission_activity,
            params.kuboard_site_name,
            params.cluster_id,
            params.namespace,
            params.username,
            params.role,
            schedule_to_close_timeout=timedelta(seconds=30),
        )
