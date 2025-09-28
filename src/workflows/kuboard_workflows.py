from datetime import timedelta
from dataclasses import dataclass, field
from typing import Optional
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
    namespaces: list[str]  # 只需要命名空间名称列表
    ldap_user_name: str  # 统一的用户配置
    role: str  # 统一的角色配置

    def __post_init__(self):
        """在创建实例后立即验证参数，如果无效立即抛出RuntimeError"""
        if not self.namespaces or len(self.namespaces) == 0:
            raise RuntimeError(f"参数错误：namespaces不能为空或未提供")

        if not all(isinstance(ns, str) for ns in self.namespaces):
            raise RuntimeError(f"参数错误：namespaces列表中的每个元素必须是字符串")

        if not self.cluster_id:
            raise RuntimeError(f"参数错误：cluster_id不能为空")


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
                    "NamespaceNotFoundError",
                    "RuntimeError",  # Failed decoding arguments 通常是 RuntimeError
                ],
            ),
        )


@workflow.defn
class KuboardNamespaceCreate:
    @workflow.run
    async def run(self, params: KuboardNamespaceCreateParams):
        """
        批量创建命名空间并授权的工作流。

        参数验证确保：
        - 所有decode参数错误由dataclass.__post_init__捕获
        - retry_policy.non_retryable_error_types确保不重试
        """
        # 执行实际的业务逻辑
        await workflow.execute_activity(
            "create_namespaces_and_grant_permissions_activity",
            params,
            schedule_to_close_timeout=timedelta(seconds=300),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
                non_retryable_error_types=[
                    "NamespaceAlreadyExistsError",
                    "RuntimeError",  # 捕获 Failed decoding arguments
                    "TypeError",  # 处理参数类型错误
                    "ValueError",  # 处理参数验证错误
                ],
            ),
        )
