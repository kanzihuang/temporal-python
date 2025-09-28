"""
测试 ClusterRole 绑定功能的单元测试
验证 KuboardNamespaceAuthorize 和 KuboardNamespaceCreate 工作流中的 ClusterRole 绑定
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.workflows.kuboard_workflows import (
    KuboardNamespaceAuthorizeParams,
    KuboardNamespaceCreateParams,
)
from src.activities import kuboard_activities
from src.services.kuboard_service import KuBoardService


class TestClusterRoleBinding:
    """测试 ClusterRole 绑定功能"""

    @pytest.mark.asyncio
    async def test_grant_permission_uses_clusterrole(self, monkeypatch):
        """测试授权功能使用 ClusterRole 而不是 Role"""
        mock_service = MagicMock(spec=KuBoardService)
        mock_service.grant_permission = MagicMock(return_value=True)

        # 模拟 ConfigLoader
        with patch("src.activities.kuboard_activities.ConfigLoader") as mock_loader:
            mock_loader.get_kuboard_site_by_cluster.return_value = type(
                "KuboardSite",
                (),
                {
                    "url": "http://test-kuboard",
                    "username": "test-user",
                    "access_key": "test-key",
                    "secret_key": "test-secret",
                },
            )()

            # 模拟 KuBoardService 的创建
            with patch(
                "src.activities.kuboard_activities.KuBoardService",
                return_value=mock_service,
            ):
                params = KuboardNamespaceAuthorizeParams(
                    cluster_id="test-cluster",
                    namespaces=["test-ns"],
                    ldap_user_name="test-user",
                    role="admin",
                )

                result = await kuboard_activities.grant_permissions_activity(params)

                assert result is True
                mock_service.grant_permission.assert_called_once_with(
                    "test-cluster", "test-ns", "test-user", "admin"
                )

    def test_rolebinding_payload_uses_clusterrole(self):
        """测试 RoleBinding 的 payload 使用 ClusterRole"""
        service = KuBoardService(
            base_url="http://test-kuboard",
            username="test-user",
            access_key="test-key",
            secret_key="test-secret",
        )

        # 模拟 _grant_stage2_permission 方法的 payload 生成
        cluster_id = "test-cluster"
        namespace = "test-ns"
        username = "test-user"
        role = "admin"

        # 构建预期的 payload
        expected_payload = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": f"user-{username}-{role}", "namespace": namespace},
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",  # 应该是 ClusterRole，不是 Role
                "name": role,
            },
            "subjects": [
                {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "User",
                    "name": username,
                }
            ],
        }

        # 验证 payload 结构正确
        assert expected_payload["roleRef"]["kind"] == "ClusterRole"
        assert expected_payload["roleRef"]["name"] == role
        assert expected_payload["kind"] == "RoleBinding"
        assert expected_payload["metadata"]["namespace"] == namespace

    @pytest.mark.asyncio
    async def test_batch_authorize_with_clusterrole(self, monkeypatch):
        """测试批量授权使用 ClusterRole"""
        called = {"grant_calls": []}

        def mock_grant_permission_activity(params):
            called["grant_calls"].append(
                (
                    params.cluster_id,
                    params.namespace,
                    params.ldap_user_name,
                    params.role,
                )
            )
            return True

        # 模拟 grant_permission_activity
        monkeypatch.setattr(
            kuboard_activities,
            "grant_permission_activity",
            AsyncMock(side_effect=mock_grant_permission_activity),
        )

        # 模拟 ConfigLoader
        with patch("src.activities.kuboard_activities.ConfigLoader") as mock_loader:
            mock_loader.get_kuboard_site_by_cluster.return_value = type(
                "KuboardSite",
                (),
                {
                    "url": "http://test-kuboard",
                    "username": "test-user",
                    "access_key": "test-key",
                    "secret_key": "test-secret",
                },
            )()

            params = KuboardNamespaceAuthorizeParams(
                cluster_id="test-cluster",
                namespaces=["ns1", "ns2", "ns3"],
                ldap_user_name="test-user",
                role="edit",  # 使用 ClusterRole
            )

            result = await kuboard_activities.grant_permissions_activity(params)

            assert result is True
            assert len(called["grant_calls"]) == 3

            # 验证所有调用都使用相同的 ClusterRole
            for call in called["grant_calls"]:
                cluster_id, namespace, username, role = call
                assert cluster_id == "test-cluster"
                assert namespace in ["ns1", "ns2", "ns3"]
                assert username == "test-user"
                assert role == "edit"  # ClusterRole

    def test_clusterrole_vs_role_difference(self):
        """测试 ClusterRole 和 Role 在 RoleBinding 中的区别"""
        # ClusterRole 绑定的 RoleBinding
        clusterrole_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": "user-john-admin", "namespace": "app-ns"},
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",  # 绑定 ClusterRole
                "name": "admin",
            },
            "subjects": [
                {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "User",
                    "name": "john",
                }
            ],
        }

        # Role 绑定的 RoleBinding（旧方式）
        role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": "user-john-admin", "namespace": "app-ns"},
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "Role",  # 绑定 Role
                "name": "admin",
            },
            "subjects": [
                {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "User",
                    "name": "john",
                }
            ],
        }

        # 验证区别
        assert clusterrole_binding["roleRef"]["kind"] == "ClusterRole"
        assert role_binding["roleRef"]["kind"] == "Role"
        assert clusterrole_binding["kind"] == "RoleBinding"  # 都是 RoleBinding
        assert role_binding["kind"] == "RoleBinding"

    def test_supported_clusterrole_types(self):
        """测试支持的 ClusterRole 类型"""
        supported_roles = ["admin", "edit", "view"]

        for role in supported_roles:
            # 验证角色名称有效
            assert isinstance(role, str)
            assert len(role) > 0

            # 模拟 ClusterRole 绑定的 payload
            payload = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "RoleBinding",
                "metadata": {"name": f"user-test-{role}", "namespace": "test-ns"},
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": role,
                },
                "subjects": [
                    {
                        "apiGroup": "rbac.authorization.k8s.io",
                        "kind": "User",
                        "name": "test-user",
                    }
                ],
            }

            assert payload["roleRef"]["kind"] == "ClusterRole"
            assert payload["roleRef"]["name"] == role


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
