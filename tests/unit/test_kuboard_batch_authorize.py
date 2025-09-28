"""
测试 KuboardNamespaceAuthorize 工作流的批量授权功能
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.workflows.kuboard_workflows import KuboardNamespaceAuthorizeParams
from src.activities import kuboard_activities


class TestKuboardBatchAuthorize:
    """测试批量授权功能"""

    @pytest.mark.asyncio
    async def test_batch_authorize_success(self, monkeypatch):
        """测试批量授权成功场景"""
        called = {"grant_calls": []}

        class FakeService:
            def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
                called["grant_calls"].append(
                    (cluster_id, namespace, ldap_user_name, role)
                )
                return True

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
                role="admin",
            )

            result = await kuboard_activities.grant_permissions_activity(params)

            assert result is True
            assert len(called["grant_calls"]) == 3

            # 验证每个命名空间都被正确授权
            expected_calls = [
                ("test-cluster", "ns1", "test-user", "admin"),
                ("test-cluster", "ns2", "test-user", "admin"),
                ("test-cluster", "ns3", "test-user", "admin"),
            ]
            assert called["grant_calls"] == expected_calls

    @pytest.mark.asyncio
    async def test_batch_authorize_partial_failure(self, monkeypatch):
        """测试批量授权部分失败场景"""
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
            # 第二个命名空间授权失败
            if params.namespace == "ns2":
                raise Exception("授权失败")
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
                role="admin",
            )

            # 应该抛出异常，因为部分授权失败
            with pytest.raises(Exception, match="批量授权完成，成功: 2，失败: 1"):
                await kuboard_activities.grant_permissions_activity(params)

            assert len(called["grant_calls"]) == 3

    @pytest.mark.asyncio
    async def test_batch_authorize_all_failure(self, monkeypatch):
        """测试批量授权全部失败场景"""
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
            raise Exception("所有授权失败")

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
                namespaces=["ns1", "ns2"],
                ldap_user_name="test-user",
                role="admin",
            )

            # 应该抛出异常，因为所有授权失败
            with pytest.raises(Exception, match="批量授权完成，成功: 0，失败: 2"):
                await kuboard_activities.grant_permissions_activity(params)

            assert len(called["grant_calls"]) == 2

    def test_kuboard_namespace_authorize_params_validation(self):
        """测试 KuboardNamespaceAuthorizeParams 参数验证"""
        # 测试空命名空间列表
        with pytest.raises(RuntimeError, match="参数错误：namespaces不能为空或未提供"):
            KuboardNamespaceAuthorizeParams(
                cluster_id="test-cluster",
                namespaces=[],
                ldap_user_name="test-user",
                role="admin",
            )

        # 测试空 cluster_id
        with pytest.raises(RuntimeError, match="参数错误：cluster_id不能为空"):
            KuboardNamespaceAuthorizeParams(
                cluster_id="",
                namespaces=["ns1"],
                ldap_user_name="test-user",
                role="admin",
            )

        # 测试空 ldap_user_name
        with pytest.raises(RuntimeError, match="参数错误：ldap_user_name不能为空"):
            KuboardNamespaceAuthorizeParams(
                cluster_id="test-cluster",
                namespaces=["ns1"],
                ldap_user_name="",
                role="admin",
            )

        # 测试空 role
        with pytest.raises(RuntimeError, match="参数错误：role不能为空"):
            KuboardNamespaceAuthorizeParams(
                cluster_id="test-cluster",
                namespaces=["ns1"],
                ldap_user_name="test-user",
                role="",
            )

        # 测试非字符串命名空间
        with pytest.raises(
            RuntimeError, match="参数错误：namespaces列表中的每个元素必须是字符串"
        ):
            KuboardNamespaceAuthorizeParams(
                cluster_id="test-cluster",
                namespaces=["ns1", 123],
                ldap_user_name="test-user",
                role="admin",
            )

    def test_kuboard_namespace_authorize_params_valid(self):
        """测试 KuboardNamespaceAuthorizeParams 有效参数"""
        params = KuboardNamespaceAuthorizeParams(
            cluster_id="test-cluster",
            namespaces=["ns1", "ns2", "ns3"],
            ldap_user_name="test-user",
            role="admin",
        )

        assert params.cluster_id == "test-cluster"
        assert params.namespaces == ["ns1", "ns2", "ns3"]
        assert params.ldap_user_name == "test-user"
        assert params.role == "admin"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
