from dataclasses import dataclass
from temporalio import activity
from src.services.kuboard_service import (
    KuBoardService,
    NamespaceAlreadyExistsError,
    NamespaceNotFoundError,
    KuboardAuthError,
    KuboardNetworkError
)
from src.shared.config import ConfigLoader
from src.workflows.kuboard_workflows import GrantPermissionParams


@dataclass
class CreateNamespaceParams:
    cluster_id: str
    namespace: str


@activity.defn
async def create_namespace_activity(params: CreateNamespaceParams) -> bool:
    try:
        # 根据 cluster_id 从配置映射中获取 KuBoard 站点信息
        kuboard_site = ConfigLoader.get_kuboard_site_by_cluster(params.cluster_id)
        service = KuBoardService(
            base_url=kuboard_site.url,
            username=kuboard_site.username,
            access_key=kuboard_site.access_key,
            secret_key=kuboard_site.secret_key
        )

        # 直接调用，如果失败会抛出异常
        service.create_namespace(params.cluster_id, params.namespace)

        return True

    except NamespaceAlreadyExistsError:
        # 命名空间已存在，直接抛出异常（不重试）
        raise
    except Exception as e:
        # 其他错误，重新抛出异常，让 Temporal 处理重试
        raise Exception(f"创建命名空间时发生错误: {str(e)}")


@activity.defn
async def grant_permission_activity(params: GrantPermissionParams) -> bool:
    try:
        # 根据 cluster_id 从配置映射中获取 KuBoard 站点信息
        kuboard_site = ConfigLoader.get_kuboard_site_by_cluster(params.cluster_id)
        service = KuBoardService(
            base_url=kuboard_site.url,
            username=kuboard_site.username,
            access_key=kuboard_site.access_key,
            secret_key=kuboard_site.secret_key
        )

        # 直接调用，如果失败会抛出异常
        service.grant_permission(
            params.cluster_id,
            params.namespace,
            params.ldap_user_name,
            params.role
        )

        return True

    except NamespaceNotFoundError:
        # 命名空间不存在，直接抛出异常（不重试）
        raise
    except (KuboardAuthError, KuboardNetworkError):
        # 重新抛出，让 Temporal 处理重试
        raise
    except Exception as e:
        # 其他错误，重新抛出异常
        raise Exception(f"授权过程中发生错误: {str(e)}")
