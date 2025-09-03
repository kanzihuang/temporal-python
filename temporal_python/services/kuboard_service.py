import requests
import json
from typing import Optional

class KuBoardService:
    def __init__(self, base_url: str = "http://kuboard.test.com:8089", 
                 username: str = "admin", 
                 access_key: str = "4xwi4exitskn",
                 secret_key: str = "j4na3jmcrdext5xfcr74pdcw4shx7wsd"):
        self.base_url = base_url
        self.username = username
        self.access_key = access_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': f'KuboardUsername={username}; KuboardAccessKey={access_key}.{secret_key}'
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
                error_msg = f"创建命名空间失败: HTTP {response.status_code}, {response.text}"
                print(f"[KuBoardService] {error_msg}")
                raise NamespaceCreationError(error_msg)
                
        except requests.exceptions.RequestException as e:
            # 网络错误，需要重试
            error_msg = f"网络错误: {str(e)}"
            print(f"[KuBoardService] {error_msg}")
            raise NamespaceCreationError(error_msg)

    def grant_permission(self, cluster_id: str, namespace: str, username: str, role: str) -> bool:
        """
        调用 KuBoard API 给用户授权（admin/edit/view）。
        """
        # TODO: 实现实际的 API 调用
        print(f"[KuBoardService] 授权: {cluster_id=} {namespace=} {username=} {role=}")
        return True

class NamespaceAlreadyExistsError(Exception):
    """命名空间已存在的异常"""
    pass

class NamespaceCreationError(Exception):
    """命名空间创建失败的异常"""
    pass



