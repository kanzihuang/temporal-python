from datetime import timedelta
from dataclasses import dataclass
from temporalio import workflow
from temporalio.common import RetryPolicy


@dataclass
class CreateNamespaceParams:
    # kuboard_site_name 通过 cluster_id 映射解析
    cluster_id: str
    namespace: str


@dataclass
class GrantPermissionParams:
    # kuboard_site_name 通过 cluster_id 映射解析
    cluster_id: str
    namespace: str
    ldap_user_name: str
    role: str


@dataclass
class KuboardNamespaceCreateParams:
    # kuboard_site_name 参数删除，运行时根据 cluster_id 解析
    cluster_id: str
    namespace: str
    ldap_user_name: str
    role: str


@workflow.defn
class KuboardNamespaceAuthorize:
    @workflow.run
    async def run(self, params: GrantPermissionParams):
        # 仅授权，要求命名空间已存在
        await workflow.execute_activity(
            "grant_permission_activity",
            params,
            schedule_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
                non_retryable_error_types=[
                    "NamespaceNotFoundError"
                ]
            )
        )


@workflow.defn
class KuboardNamespaceCreate:
    @workflow.run
    async def run(self, params: KuboardNamespaceCreateParams):
        # 1. 创建命名空间（如果已存在则报错）
        try:
            create_params = CreateNamespaceParams(
                cluster_id=params.cluster_id,
                namespace=params.namespace
            )
            await workflow.execute_activity(
                "create_namespace_activity",
                create_params,
                schedule_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                    non_retryable_error_types=[
                        "NamespaceAlreadyExistsError"
                    ]
                )
            )
        except Exception as e:
            # 检查是否是命名空间已存在的异常
            if "NamespaceAlreadyExistsError" in str(type(e).__name__):
                # 命名空间已存在，抛出异常
                raise
            # 其他错误，重新抛出
            raise
        # 2. 授权
        grant_params = GrantPermissionParams(
            cluster_id=params.cluster_id,
            namespace=params.namespace,
            ldap_user_name=params.ldap_user_name,
            role=params.role
        )
        await workflow.execute_activity(
            "grant_permission_activity",
            grant_params,
            schedule_to_close_timeout=timedelta(seconds=30),
        )
