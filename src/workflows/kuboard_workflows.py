from datetime import timedelta
from dataclasses import dataclass
from temporalio import workflow
from temporalio.common import RetryPolicy
from src.shared.config import ConfigLoader


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
        # 先校验 cluster 是否能映射到 Kuboard 站点
        try:
            _ = ConfigLoader.get_kuboard_site_by_cluster(params.cluster_id)
        except Exception:
            # 按要求返回中文提示
            raise RuntimeError("由于权限不足，系统授权失败，将由运维人员手动授权。")

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
        # 0. 解析 kuboard_site_name（若失败则返回错误，提示人工介入）
        try:
            kuboard_site = ConfigLoader.get_kuboard_site_by_cluster(params.cluster_id)
            kuboard_site_name = kuboard_site.name
        except Exception as e:
            # 按要求返回中文提示
            raise RuntimeError("由于权限不足，系统创建命名空间失败，将由运维人员手动创建命名空间。")

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
