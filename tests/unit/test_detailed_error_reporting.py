"""
测试详细的错误信息报告功能
验证批量操作失败时提供的详细错误信息
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.workflows.kuboard_workflows import (
    KuboardNamespaceAuthorizeParams,
    KuboardNamespaceCreateParams,
)
from src.activities import kuboard_activities


class TestDetailedErrorReporting:
    """测试详细错误信息报告功能"""

    @pytest.mark.asyncio
    async def test_batch_authorize_detailed_error_message(self, monkeypatch):
        """测试批量授权失败时的详细错误信息"""
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
                raise Exception("ClusterRole 'admin' 不存在")
            # 第三个命名空间授权失败
            if params.namespace == "ns3":
                raise Exception("命名空间不存在")
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
                namespaces=["ns1", "ns2", "ns3", "ns4"],
                ldap_user_name="test-user",
                role="admin",
            )

            # 应该抛出包含详细信息的异常
            with pytest.raises(Exception) as exc_info:
                await kuboard_activities.grant_permissions_activity(params)

            error_message = str(exc_info.value)

            # 验证错误信息包含详细内容
            assert "批量授权完成，成功: 2，失败: 2" in error_message
            assert "成功的命名空间: ['ns1', 'ns4']" in error_message
            assert "失败的命名空间: ['ns2', 'ns3']" in error_message
            assert "详细错误信息:" in error_message
            assert "ns2: 授权失败: ClusterRole 'admin' 不存在" in error_message
            assert "ns3: 授权失败: 命名空间不存在" in error_message

    @pytest.mark.asyncio
    async def test_batch_create_detailed_error_message(self, monkeypatch):
        """测试批量创建命名空间失败时的详细错误信息"""
        called = {"create_calls": [], "grant_calls": []}

        def mock_create_namespace_activity(params):
            called["create_calls"].append((params.cluster_id, params.namespace))
            # 第二个命名空间创建失败
            if params.namespace == "ns2":
                raise Exception("命名空间已存在")
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
            # 第三个命名空间授权失败
            if params.namespace == "ns3":
                raise Exception("用户权限不足")
            return True

        # 模拟活动函数
        monkeypatch.setattr(
            kuboard_activities,
            "create_namespace_activity",
            AsyncMock(side_effect=mock_create_namespace_activity),
        )
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

            params = KuboardNamespaceCreateParams(
                cluster_id="test-cluster",
                namespaces=["ns1", "ns2", "ns3"],
                ldap_user_name="test-user",
                role="admin",
            )

            # 应该抛出包含详细信息的异常
            with pytest.raises(Exception) as exc_info:
                await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                    params
                )

            error_message = str(exc_info.value)

            # 验证错误信息包含详细内容
            assert "批量处理完成，成功: 1，失败: 2" in error_message
            assert "成功的命名空间: ['ns1']" in error_message
            assert "失败的命名空间: ['ns2', 'ns3']" in error_message
            assert "详细错误信息:" in error_message
            assert "ns2: 处理失败: 命名空间已存在" in error_message
            assert "ns3: 处理失败: 用户权限不足" in error_message

    @pytest.mark.asyncio
    async def test_all_failure_detailed_error_message(self, monkeypatch):
        """测试全部失败时的详细错误信息"""

        def mock_grant_permission_activity(params):
            raise Exception("所有授权失败：网络连接超时")

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

            # 应该抛出包含详细信息的异常
            with pytest.raises(Exception) as exc_info:
                await kuboard_activities.grant_permissions_activity(params)

            error_message = str(exc_info.value)

            # 验证错误信息包含详细内容
            assert "批量授权完成，成功: 0，失败: 2" in error_message
            assert "成功的命名空间: []" in error_message
            assert "失败的命名空间: ['ns1', 'ns2']" in error_message
            assert "详细错误信息:" in error_message
            assert "ns1: 授权失败: 所有授权失败：网络连接超时" in error_message
            assert "ns2: 授权失败: 所有授权失败：网络连接超时" in error_message

    def test_error_message_structure(self):
        """测试错误信息结构的完整性"""
        # 模拟错误信息结构
        successful_namespaces = ["ns1", "ns3"]
        failed_namespaces = ["ns2", "ns4"]
        error_details = [
            "ns2: 授权失败: ClusterRole 不存在",
            "ns4: 授权失败: 命名空间不存在",
        ]

        error_summary = (
            f"批量授权完成，成功: 2，失败: 2。"
            f"成功的命名空间: {successful_namespaces}。"
            f"失败的命名空间: {failed_namespaces}。"
            f"详细错误信息: {'; '.join(error_details)}"
        )

        # 验证错误信息结构
        assert "批量授权完成，成功: 2，失败: 2" in error_summary
        assert "成功的命名空间: ['ns1', 'ns3']" in error_summary
        assert "失败的命名空间: ['ns2', 'ns4']" in error_summary
        assert (
            "详细错误信息: ns2: 授权失败: ClusterRole 不存在; ns4: 授权失败: 命名空间不存在"
            in error_summary
        )

    @pytest.mark.asyncio
    async def test_single_namespace_failure(self, monkeypatch):
        """测试单个命名空间失败时的错误信息"""

        def mock_grant_permission_activity(params):
            if params.namespace == "single-ns":
                raise Exception("单个命名空间失败")
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
                namespaces=["single-ns"],
                ldap_user_name="test-user",
                role="admin",
            )

            # 应该抛出包含详细信息的异常
            with pytest.raises(Exception) as exc_info:
                await kuboard_activities.grant_permissions_activity(params)

            error_message = str(exc_info.value)

            # 验证错误信息包含详细内容
            assert "批量授权完成，成功: 0，失败: 1" in error_message
            assert "成功的命名空间: []" in error_message
            assert "失败的命名空间: ['single-ns']" in error_message
            assert (
                "详细错误信息: single-ns: 授权失败: 单个命名空间失败" in error_message
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
