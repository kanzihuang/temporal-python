import pytest
from src.activities import kuboard_activities
from src.workflows.kuboard_workflows import KuboardNamespaceCreateParams
from src.services.kuboard_service import NamespaceAlreadyExistsError


class TestBatchNamespaceProcessing:
    """批量命名空间处理测试类"""

    @pytest.mark.asyncio
    async def test_batch_processing_success_all_new_namespaces(self, monkeypatch):
        """测试批量处理成功 - 所有命名空间都是新的"""
        called = {"create_calls": [], "grant_calls": []}

        class FakeService:
            def create_namespace(self, cluster_id, namespace):
                called["create_calls"].append((cluster_id, namespace))
                return True

            def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
                called["grant_calls"].append(
                    (cluster_id, namespace, ldap_user_name, role)
                )
                return True

        self._setup_mocks(monkeypatch, FakeService)

        params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=["new-ns1", "new-ns2", "new-ns3"],
            ldap_user_name="test-user",
            role="admin",
        )

        result = (
            await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                params
            )
        )

        assert result is True
        assert len(called["create_calls"]) == 3
        assert len(called["grant_calls"]) == 3

        # 验证创建调用
        expected_create_calls = [
            ("test-cluster", "new-ns1"),
            ("test-cluster", "new-ns2"),
            ("test-cluster", "new-ns3"),
        ]
        assert called["create_calls"] == expected_create_calls

        # 验证授权调用
        expected_grant_calls = [
            ("test-cluster", "new-ns1", "test-user", "admin"),
            ("test-cluster", "new-ns2", "test-user", "admin"),
            ("test-cluster", "new-ns3", "test-user", "admin"),
        ]
        assert called["grant_calls"] == expected_grant_calls

    @pytest.mark.asyncio
    async def test_batch_processing_mixed_existing_and_new(self, monkeypatch):
        """测试批量处理 - 混合已存在和新的命名空间"""
        called = {"create_calls": [], "grant_calls": []}

        class FakeService:
            def create_namespace(self, cluster_id, namespace):
                called["create_calls"].append((cluster_id, namespace))
                if namespace == "existing-ns":
                    raise NamespaceAlreadyExistsError("命名空间已存在")
                return True

            def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
                called["grant_calls"].append(
                    (cluster_id, namespace, ldap_user_name, role)
                )
                return True

        self._setup_mocks(monkeypatch, FakeService)

        params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=["new-ns1", "existing-ns", "new-ns2"],
            ldap_user_name="test-user",
            role="edit",
        )

        result = (
            await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                params
            )
        )

        assert result is True
        # 所有命名空间都应该尝试创建
        assert len(called["create_calls"]) == 3
        # 所有命名空间都应该授权（包括已存在的）
        assert len(called["grant_calls"]) == 3

    @pytest.mark.asyncio
    async def test_batch_processing_partial_failure(self, monkeypatch):
        """测试批量处理 - 部分失败"""
        called = {"create_calls": [], "grant_calls": []}

        class FakeService:
            def create_namespace(self, cluster_id, namespace):
                called["create_calls"].append((cluster_id, namespace))
                if namespace == "failing-ns":
                    raise Exception("创建失败")
                return True

            def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
                called["grant_calls"].append(
                    (cluster_id, namespace, ldap_user_name, role)
                )
                return True

        self._setup_mocks(monkeypatch, FakeService)

        params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=["success-ns1", "failing-ns", "success-ns2"],
            ldap_user_name="test-user",
            role="viewer",
        )

        with pytest.raises(Exception, match="批量处理完成，成功: 2，失败: 1"):
            await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                params
            )

    @pytest.mark.asyncio
    async def test_batch_processing_empty_namespace_list(self, monkeypatch):
        """测试批量处理 - 空命名空间列表"""
        called = {"create_calls": [], "grant_calls": []}

        class FakeService:
            def create_namespace(self, cluster_id, namespace):
                called["create_calls"].append((cluster_id, namespace))
                return True

            def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
                called["grant_calls"].append(
                    (cluster_id, namespace, ldap_user_name, role)
                )
                return True

        self._setup_mocks(monkeypatch, FakeService)

        params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=[],
            ldap_user_name="test-user",
            role="admin",
        )

        result = (
            await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                params
            )
        )

        assert result is True
        assert len(called["create_calls"]) == 0
        assert len(called["grant_calls"]) == 0

    @pytest.mark.asyncio
    async def test_batch_processing_single_namespace(self, monkeypatch):
        """测试批量处理 - 单个命名空间"""
        called = {"create_calls": [], "grant_calls": []}

        class FakeService:
            def create_namespace(self, cluster_id, namespace):
                called["create_calls"].append((cluster_id, namespace))
                return True

            def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
                called["grant_calls"].append(
                    (cluster_id, namespace, ldap_user_name, role)
                )
                return True

        self._setup_mocks(monkeypatch, FakeService)

        params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=["single-ns"],
            ldap_user_name="test-user",
            role="admin",
        )

        result = (
            await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                params
            )
        )

        assert result is True
        assert len(called["create_calls"]) == 1
        assert len(called["grant_calls"]) == 1
        assert called["create_calls"][0] == ("test-cluster", "single-ns")
        assert called["grant_calls"][0] == (
            "test-cluster",
            "single-ns",
            "test-user",
            "admin",
        )

    @pytest.mark.asyncio
    async def test_batch_processing_different_roles(self, monkeypatch):
        """测试批量处理 - 不同角色"""
        called = {"create_calls": [], "grant_calls": []}

        class FakeService:
            def create_namespace(self, cluster_id, namespace):
                called["create_calls"].append((cluster_id, namespace))
                return True

            def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
                called["grant_calls"].append(
                    (cluster_id, namespace, ldap_user_name, role)
                )
                return True

        self._setup_mocks(monkeypatch, FakeService)

        # 测试 admin 角色
        admin_params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=["ns1", "ns2"],
            ldap_user_name="admin-user",
            role="admin",
        )

        result = (
            await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                admin_params
            )
        )
        assert result is True

        # 验证所有授权调用都使用 admin 角色
        for call in called["grant_calls"]:
            assert call[3] == "admin"  # role 参数

        # 重置调用记录
        called["create_calls"] = []
        called["grant_calls"] = []

        # 测试 edit 角色
        edit_params = KuboardNamespaceCreateParams(
            cluster_id="test-cluster",
            namespaces=["ns3", "ns4"],
            ldap_user_name="edit-user",
            role="edit",
        )

        result = (
            await kuboard_activities.create_namespaces_and_grant_permissions_activity(
                edit_params
            )
        )
        assert result is True

        # 验证所有授权调用都使用 edit 角色
        for call in called["grant_calls"]:
            assert call[3] == "edit"  # role 参数

    def _setup_mocks(self, monkeypatch, service_class):
        """设置测试用的 mock 对象"""
        monkeypatch.setattr(
            kuboard_activities, "KuBoardService", lambda **kwargs: service_class()
        )
        monkeypatch.setattr(
            kuboard_activities,
            "ConfigLoader",
            type(
                "MockConfigLoader",
                (),
                {
                    "get_kuboard_site_by_cluster": lambda cluster_id: type(
                        "MockSite",
                        (),
                        {
                            "url": "http://test.com",
                            "username": "admin",
                            "access_key": "test-access-key",
                            "secret_key": "test-secret-key",
                        },
                    )()
                },
            ),
        )
