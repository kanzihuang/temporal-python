import requests


class KuBoardService:
    def __init__(self, base_url: str, username: str, access_key: str, secret_key: str):
        self.base_url = base_url
        self.username = username
        self.access_key = access_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': f'KuboardUsername={username}; '
                      f'KuboardAccessKey={access_key}.{secret_key}'
        })

    def create_namespace(self, cluster_id: str, namespace: str) -> bool:
        """
        调用 KuBoard API 创建命名空间。
        如果命名空间已存在，抛出异常。
        如果其他错误，按重试策略重试。
        """
        url = f"{self.base_url}/k8s-api/{cluster_id}/api/v1/namespaces"
        payload = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": namespace
            }
        }

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 201:
                # 创建成功
                print(f"[KuBoardService] 命名空间创建成功: {cluster_id=} {namespace=}")
                return True
            elif response.status_code == 409:
                # 命名空间已存在
                error_msg = f"命名空间已存在: {namespace}"
                print(f"[KuBoardService] {error_msg}")
                raise NamespaceAlreadyExistsError(error_msg)
            else:
                # 其他错误，需要重试
                error_msg = (f"创建命名空间失败: HTTP {response.status_code}, "
                             f"{response.text}")
                print(f"[KuBoardService] {error_msg}")
                raise NamespaceCreationError(error_msg)

        except requests.exceptions.RequestException as e:
            # 网络错误，需要重试
            error_msg = f"网络错误: {str(e)}"
            print(f"[KuBoardService] {error_msg}")
            raise NamespaceCreationError(error_msg)

    def grant_permission(self, cluster_id: str, namespace: str,
                         username: str, role: str) -> bool:
        """
        调用 KuBoard API 给用户授权（admin/edit/view）。
        包含两个阶段：
        1. 第一阶段：创建 KuboardAuthClusterRoleBinding，绑定 viewer 角色
        2. 第二阶段：创建 RoleBinding，绑定指定角色到指定命名空间
        """
        # 第一阶段授权：创建 KuboardAuthClusterRoleBinding，绑定 viewer 角色
        self._grant_stage1_permission(cluster_id, username)

        # 第二阶段授权：创建 RoleBinding，绑定指定角色到指定命名空间
        self._grant_stage2_permission(cluster_id, namespace, username, role)

        print(f"[KuBoardService] 授权成功: {cluster_id=} {namespace=} "
              f"{username=} {role=}")
        return True

    def _grant_stage1_permission(self, cluster_id: str, username: str) -> None:
        """
        第一阶段授权：创建 KuboardAuthClusterRoleBinding，绑定 viewer 角色
        """
        url = (f"{self.base_url}/kuboard-api/cluster/{cluster_id}/"
               f"kind/KuboardAuthClusterRoleBinding")
        payload = {
            "kind": "KuboardAuthClusterRoleBinding",
            "metadata": {
                "cluster": cluster_id,
                "name": f"user.{username}.viewer"
            },
            "spec": {
                "subject": {
                    "kind": "KuboardAuthUser",
                    "name": username
                },
                "role": {
                    "name": "viewer"
                }
            }
        }

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                print(f"[KuBoardService] 第一阶段授权成功: {cluster_id=} {username=}")
            elif response.status_code == 500 and "对象已存在" in response.text:
                print(f"[KuBoardService] 第一阶段授权已存在: "
                      f"{cluster_id=} {username=}")
            else:
                error_msg = (f"第一阶段授权失败: HTTP {response.status_code}, "
                             f"{response.text}")
                print(f"[KuBoardService] {error_msg}")
                raise KuboardAuthError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"第一阶段授权网络错误: {str(e)}"
            print(f"[KuBoardService] {error_msg}")
            raise KuboardNetworkError(error_msg)
        except Exception as e:
            if "对象已存在" in str(e):
                print(f"[KuBoardService] 第一阶段授权已存在: "
                      f"{cluster_id=} {username=}")
            else:
                raise

    def _grant_stage2_permission(self, cluster_id: str, namespace: str,
                                 username: str, role: str) -> None:
        """
        第二阶段授权：创建 RoleBinding，绑定指定角色到指定命名空间
        """
        url = (f"{self.base_url}/k8s-api/{cluster_id}/apis/"
               f"rbac.authorization.k8s.io/v1/namespaces/"
               f"{namespace}/rolebindings")
        payload = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": f"user-{username}-{role}",
                "namespace": namespace
            },
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "Role",
                "name": role
            },
            "subjects": [
                {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "User",
                    "name": username
                }
            ]
        }

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 201:
                print(f"[KuBoardService] 第二阶段授权成功: "
                      f"{cluster_id=} {namespace=} {username=} {role=}")
            elif response.status_code == 409 and "already exists" in response.text:
                print(f"[KuBoardService] 第二阶段授权已存在: "
                      f"{cluster_id=} {namespace=} {username=} {role=}")
            elif response.status_code == 404:
                # 命名空间不存在
                error_msg = f"命名空间不存在: {namespace}"
                print(f"[KuBoardService] {error_msg}")
                raise NamespaceNotFoundError(error_msg)
            else:
                error_msg = (f"第二阶段授权失败: HTTP {response.status_code}, "
                             f"{response.text}")
                print(f"[KuBoardService] {error_msg}")
                raise KuboardAuthError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"第二阶段授权网络错误: {str(e)}"
            print(f"[KuBoardService] {error_msg}")
            raise KuboardNetworkError(error_msg)
        except Exception as e:
            if "already exists" in str(e):
                print(f"[KuBoardService] 第二阶段授权已存在: "
                      f"{cluster_id=} {namespace=} {username=} {role=}")
            else:
                raise


class NamespaceAlreadyExistsError(Exception):
    """命名空间已存在的异常"""
    pass


class NamespaceCreationError(Exception):
    """命名空间创建失败的异常"""
    pass


class KuboardAuthError(Exception):
    """Kuboard 授权相关错误"""
    pass


class KuboardNetworkError(Exception):
    """Kuboard 网络错误"""
    pass


class KuboardPermissionError(Exception):
    """Kuboard 权限错误"""
    pass


class NamespaceNotFoundError(Exception):
    """命名空间不存在的异常"""
    pass
