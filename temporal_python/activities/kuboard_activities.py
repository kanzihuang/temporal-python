from temporal_python.services.kuboard_service import KuBoardService, NamespaceAlreadyExistsError, NamespaceCreationError
from temporal_python.shared.config import ConfigLoader

async def create_namespace_activity(kuboard_site_name: str, cluster_id: str, namespace: str) -> bool:
    # 从配置中获取 KuBoard 站点信息
    kuboard_site = ConfigLoader.get_kuboard_site(kuboard_site_name)
    service = KuBoardService(
        base_url=kuboard_site.url,
        username=kuboard_site.username,
        access_key=kuboard_site.access_key,
        secret_key=kuboard_site.secret_key
    )
    try:
        return service.create_namespace(cluster_id, namespace)
    except NamespaceAlreadyExistsError:
        # 命名空间已存在，直接抛出异常
        raise
    except NamespaceCreationError:
        # 其他错误，可以重试
        raise

async def grant_permission_activity(kuboard_site_name: str, cluster_id: str, namespace: str, username: str, role: str) -> bool:
    # 从配置中获取 KuBoard 站点信息
    kuboard_site = ConfigLoader.get_kuboard_site(kuboard_site_name)
    service = KuBoardService(
        base_url=kuboard_site.url,
        username=kuboard_site.username,
        access_key=kuboard_site.access_key,
        secret_key=kuboard_site.secret_key
    )
    return service.grant_permission(cluster_id, namespace, username, role)



