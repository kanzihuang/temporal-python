from temporal_python.services.kuboard_service import KuBoardService

async def create_namespace_activity(cluster_id: str, namespace: str) -> bool:
    service = KuBoardService()
    return service.create_namespace(cluster_id, namespace)

async def grant_permission_activity(cluster_id: str, namespace: str, username: str, role: str) -> bool:
    service = KuBoardService()
    return service.grant_permission(cluster_id, namespace, username, role)



