from dataclasses import dataclass
from temporalio import activity
from temporal_python.services.kuboard_service import KuBoardService, NamespaceAlreadyExistsError, NamespaceCreationError
from temporal_python.shared.config import ConfigLoader

@dataclass
class CreateNamespaceParams:
    kuboard_site_name: str
    cluster_id: str
    namespace: str

@dataclass
class GrantPermissionParams:
    kuboard_site_name: str
    cluster_id: str
    namespace: str
    username: str
    role: str

@activity.defn
async def create_namespace_activity(params: CreateNamespaceParams) -> bool:
    # 从配置中获取 KuBoard 站点信息
    kuboard_site = ConfigLoader.get_kuboard_site(params.kuboard_site_name)
    service = KuBoardService(
        base_url=kuboard_site.url,
        username=kuboard_site.username,
        access_key=kuboard_site.access_key,
        secret_key=kuboard_site.secret_key
    )
    try:
        return service.create_namespace(params.cluster_id, params.namespace)
    except NamespaceAlreadyExistsError:
        # 命名空间已存在，直接抛出异常
        raise
    except NamespaceCreationError:
        # 其他错误，可以重试
        raise

@activity.defn
async def grant_permission_activity(params: GrantPermissionParams) -> bool:
    # 从配置中获取 KuBoard 站点信息
    kuboard_site = ConfigLoader.get_kuboard_site(params.kuboard_site_name)
    service = KuBoardService(
        base_url=kuboard_site.url,
        username=kuboard_site.username,
        access_key=kuboard_site.access_key,
        secret_key=kuboard_site.secret_key
    )
    return service.grant_permission(params.cluster_id, params.namespace, params.username, params.role)



