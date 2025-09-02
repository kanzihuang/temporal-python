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

@workflow.defn
class KuboardNamespaceAuthorize:
    @workflow.run
    async def run(self, params: KuboardNamespaceAuthorizeParams):
        # 1. 创建命名空间（忽略已存在的错误）
        try:
            await workflow.execute_activity(
                create_namespace_activity,
                params.cluster_id,
                params.namespace,
                schedule_to_close_timeout=timedelta(seconds=30),
            )
        except Exception as e:
            # 假设已存在时 API 返回特定异常，可根据实际情况调整
            if "已存在" not in str(e):
                raise
        # 2. 授权
        await workflow.execute_activity(
            grant_permission_activity,
            params.cluster_id,
            params.namespace,
            params.username,
            params.role,
            schedule_to_close_timeout=timedelta(seconds=30),
        )
