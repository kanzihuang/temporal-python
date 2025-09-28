from dataclasses import dataclass
from temporalio import activity
from src.services.kuboard_service import (
    KuBoardService,
    NamespaceAlreadyExistsError,
    NamespaceNotFoundError,
    KuboardAuthError,
    KuboardNetworkError,
)
from src.shared.config import ConfigLoader
from src.workflows.kuboard_workflows import (
    GrantPermissionParams,
    KuboardNamespaceCreateParams,
    KuboardNamespaceAuthorizeParams,
)


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
            secret_key=kuboard_site.secret_key,
        )

        # 直接调用，如果失败会抛出异常
        service.create_namespace(params.cluster_id, params.namespace)

        return True

    except NamespaceAlreadyExistsError:
        # 命名空间已存在，直接抛出异常（不重试）
        raise
    except Exception as e:
        # 如果是映射失败（没有对应 Kuboard），返回指定中文提示
        msg = str(e)
        if "No kuboard_site_name mapping" in msg or "No kuboard cluster mapping" in msg:
            raise Exception(
                "由于权限不足，系统创建命名空间失败，将由运维人员手动创建命名空间。"
            )
        # 其他错误，重新抛出异常，让 Temporal 处理重试
        raise Exception(f"创建命名空间过程中发生错误: {msg}")


@activity.defn
async def grant_permission_activity(params: GrantPermissionParams) -> bool:
    try:
        # 根据 cluster_id 从配置映射中获取 KuBoard 站点信息
        kuboard_site = ConfigLoader.get_kuboard_site_by_cluster(params.cluster_id)
        service = KuBoardService(
            base_url=kuboard_site.url,
            username=kuboard_site.username,
            access_key=kuboard_site.access_key,
            secret_key=kuboard_site.secret_key,
        )

        # 直接调用，如果失败会抛出异常
        service.grant_permission(
            params.cluster_id,
            params.namespace,
            params.ldap_user_name,
            params.role,
        )

        return True

    except NamespaceNotFoundError:
        # 命名空间不存在，直接抛出异常（不重试）
        raise
    except Exception as e:
        # 如果是映射失败（没有对应 Kuboard），返回指定中文提示
        msg = str(e)
        if "No kuboard_site_name mapping" in msg or "No kuboard cluster mapping" in msg:
            raise Exception("由于权限不足，系统授权失败，将由运维人员手动授权。")
        # 其他错误，重新抛出异常
        raise Exception(f"授权过程中发生错误: {msg}")


@activity.defn
async def create_namespaces_and_grant_permissions_activity(
    params: KuboardNamespaceCreateParams,
) -> bool:
    """
    批量创建命名空间并授权的活动函数
    处理多个命名空间的创建和授权操作
    """
    try:
        # 根据 cluster_id 从配置映射中获取 KuBoard 站点信息
        kuboard_site = ConfigLoader.get_kuboard_site_by_cluster(params.cluster_id)
        service = KuBoardService(
            base_url=kuboard_site.url,
            username=kuboard_site.username,
            access_key=kuboard_site.access_key,
            secret_key=kuboard_site.secret_key,
        )

        # 存储处理结果
        results = []
        errors = []

        # 遍历所有命名空间进行处理，使用统一的用户和角色配置
        for namespace in params.namespaces:
            try:
                # 1. 创建命名空间
                create_params = CreateNamespaceParams(
                    cluster_id=params.cluster_id, namespace=namespace
                )
                await create_namespace_activity(create_params)

                # 2. 授权（使用统一的用户和角色配置）
                grant_params = GrantPermissionParams(
                    cluster_id=params.cluster_id,
                    namespace=namespace,
                    ldap_user_name=params.ldap_user_name,
                    role=params.role,
                )
                await grant_permission_activity(grant_params)

                results.append(
                    {
                        "namespace": namespace,
                        "status": "success",
                        "message": "命名空间创建和授权成功",
                    }
                )

            except NamespaceAlreadyExistsError:
                # 命名空间已存在，继续授权
                try:
                    grant_params = GrantPermissionParams(
                        cluster_id=params.cluster_id,
                        namespace=namespace,
                        ldap_user_name=params.ldap_user_name,
                        role=params.role,
                    )
                    await grant_permission_activity(grant_params)

                    results.append(
                        {
                            "namespace": namespace,
                            "status": "success",
                            "message": "命名空间已存在，授权成功",
                        }
                    )
                except Exception as grant_error:
                    errors.append(
                        {
                            "namespace": namespace,
                            "error": f"授权失败: {str(grant_error)}",
                        }
                    )

            except Exception as e:
                errors.append(
                    {
                        "namespace": namespace,
                        "error": f"处理失败: {str(e)}",
                    }
                )

        # 如果有错误，抛出异常
        if errors:
            error_summary = f"批量处理完成，成功: {len(results)}，失败: {len(errors)}"
            raise Exception(error_summary)

        return True

    except Exception as e:
        # 如果是映射失败（没有对应 Kuboard），返回指定中文提示
        msg = str(e)
        if "No kuboard_site_name mapping" in msg or "No kuboard cluster mapping" in msg:
            raise Exception("由于权限不足，系统批量处理失败，将由运维人员手动处理。")
        # 其他错误，重新抛出异常
        raise Exception(f"批量创建命名空间和授权过程中发生错误: {msg}")


@activity.defn
async def grant_permissions_activity(params: KuboardNamespaceAuthorizeParams) -> bool:
    """
    批量授权多个命名空间的活动函数
    对已存在的命名空间进行授权操作
    """
    try:
        # 根据 cluster_id 从配置映射中获取 KuBoard 站点信息
        kuboard_site = ConfigLoader.get_kuboard_site_by_cluster(params.cluster_id)
        service = KuBoardService(
            base_url=kuboard_site.url,
            username=kuboard_site.username,
            access_key=kuboard_site.access_key,
            secret_key=kuboard_site.secret_key,
        )

        # 存储处理结果
        results = []
        errors = []

        # 遍历所有命名空间进行授权，使用统一的用户和角色配置
        for namespace in params.namespaces:
            try:
                # 授权（使用统一的用户和角色配置）
                grant_params = GrantPermissionParams(
                    cluster_id=params.cluster_id,
                    namespace=namespace,
                    ldap_user_name=params.ldap_user_name,
                    role=params.role,
                )
                await grant_permission_activity(grant_params)

                results.append(
                    {
                        "namespace": namespace,
                        "status": "success",
                        "message": "命名空间授权成功",
                    }
                )

            except Exception as e:
                errors.append(
                    {
                        "namespace": namespace,
                        "error": f"授权失败: {str(e)}",
                    }
                )

        # 如果有错误，抛出异常
        if errors:
            error_summary = f"批量授权完成，成功: {len(results)}，失败: {len(errors)}"
            raise Exception(error_summary)

        return True

    except Exception as e:
        # 如果是映射失败（没有对应 Kuboard），返回指定中文提示
        msg = str(e)
        if "No kuboard_site_name mapping" in msg or "No kuboard cluster mapping" in msg:
            raise Exception("由于权限不足，系统批量授权失败，将由运维人员手动处理。")
        # 其他错误，重新抛出异常
        raise Exception(f"批量授权过程中发生错误: {msg}")
