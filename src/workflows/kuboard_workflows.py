from datetime import timedelta
from dataclasses import dataclass
from temporalio import workflow
from temporalio.common import RetryPolicy


@dataclass
class CreateNamespaceParams:
    cluster_id: str
    namespace: str


@dataclass
class GrantPermissionParams:
    cluster_id: str
    namespace: str
    ldap_user_name: str
    role: str


@dataclass
class KuboardNamespaceCreateParams:
    cluster_id: str
    namespaces: list[str]
    ldap_user_name: str
    role: str

    def __post_init__(self):
        """参数验证：确保必要参数不为空"""
        if not self.namespaces or len(self.namespaces) == 0:
            raise RuntimeError("参数错误：namespaces不能为空或未提供")

        if not all(isinstance(ns, str) for ns in self.namespaces):
            raise RuntimeError("参数错误：namespaces列表中的每个元素必须是字符串")

        if not self.cluster_id:
            raise RuntimeError("参数错误：cluster_id不能为空")


@workflow.defn(
    failure_exception_types=[
        RuntimeError,  # 捕获 Failed decoding arguments
        TypeError,  # 捕获 missing required positional argument
        ValueError,  # 捕获参数验证错误
    ]
)
class KuboardNamespaceAuthorize:
    @workflow.run
    async def run(self, params: GrantPermissionParams):
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
                    "RuntimeError",
                ],
            ),
        )


@workflow.defn(
    failure_exception_types=[
        RuntimeError,  # 捕获 Failed decoding arguments
        TypeError,  # 捕获 missing required positional argument
        ValueError,  # 捕获参数验证错误
    ]
)
class KuboardNamespaceCreate:
    @workflow.run
    async def run(self, params: KuboardNamespaceCreateParams):
        """批量创建命名空间并授权的工作流"""
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
                    "RuntimeError",
                    "TypeError",
                    "ValueError",
                ],
            ),
        )
