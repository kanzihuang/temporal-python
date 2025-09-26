import pytest
from src.activities import kuboard_activities
from src.activities.kuboard_activities import (
    CreateNamespaceParams,
    GrantPermissionParams,
)
from src.workflows.kuboard_workflows import KuboardNamespaceCreateParams


@pytest.mark.asyncio
async def test_create_namespace_activity(monkeypatch):
    called = {}

    class FakeService:
        def create_namespace(self, cluster_id, namespace):
            called["args"] = (cluster_id, namespace)
            return True

    monkeypatch.setattr(
        kuboard_activities, "KuBoardService", lambda **kwargs: FakeService()
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
    params = CreateNamespaceParams(cluster_id="c1", namespace="ns1")
    result = await kuboard_activities.create_namespace_activity(params)
    assert result is True
    assert called["args"] == ("c1", "ns1")


@pytest.mark.asyncio
async def test_grant_permission_activity(monkeypatch):
    called = {}

    class FakeService:
        def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
            called["args"] = (cluster_id, namespace, ldap_user_name, role)
            return True

    monkeypatch.setattr(
        kuboard_activities, "KuBoardService", lambda **kwargs: FakeService()
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
    params = GrantPermissionParams(
        cluster_id="c1", namespace="ns1", ldap_user_name="user", role="admin"
    )
    result = await kuboard_activities.grant_permission_activity(params)
    assert result is True
    assert called["args"] == ("c1", "ns1", "user", "admin")


@pytest.mark.asyncio
async def test_create_namespaces_and_grant_permissions_activity_success(monkeypatch):
    """测试批量创建命名空间和授权活动成功"""
    called = {"create_calls": [], "grant_calls": []}

    class FakeService:
        def create_namespace(self, cluster_id, namespace):
            called["create_calls"].append((cluster_id, namespace))
            return True

        def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
            called["grant_calls"].append((cluster_id, namespace, ldap_user_name, role))
            return True

    monkeypatch.setattr(
        kuboard_activities, "KuBoardService", lambda **kwargs: FakeService()
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

    params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2", "ns3"],
        ldap_user_name="user",
        role="admin",
    )

    result = await kuboard_activities.create_namespaces_and_grant_permissions_activity(
        params
    )
    assert result is True
    assert len(called["create_calls"]) == 3
    assert len(called["grant_calls"]) == 3
    assert called["create_calls"] == [("c1", "ns1"), ("c1", "ns2"), ("c1", "ns3")]
    assert called["grant_calls"] == [
        ("c1", "ns1", "user", "admin"),
        ("c1", "ns2", "user", "admin"),
        ("c1", "ns3", "user", "admin"),
    ]


@pytest.mark.asyncio
async def test_create_namespaces_and_grant_permissions_activity_with_existing_namespace(
    monkeypatch,
):
    """测试批量处理时遇到已存在的命名空间"""
    called = {"create_calls": [], "grant_calls": []}

    class FakeService:
        def create_namespace(self, cluster_id, namespace):
            called["create_calls"].append((cluster_id, namespace))
            if namespace == "ns2":
                from src.services.kuboard_service import NamespaceAlreadyExistsError

                raise NamespaceAlreadyExistsError("命名空间已存在")
            return True

        def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
            called["grant_calls"].append((cluster_id, namespace, ldap_user_name, role))
            return True

    monkeypatch.setattr(
        kuboard_activities, "KuBoardService", lambda **kwargs: FakeService()
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

    params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2", "ns3"],
        ldap_user_name="user",
        role="admin",
    )

    result = await kuboard_activities.create_namespaces_and_grant_permissions_activity(
        params
    )
    assert result is True
    # 所有命名空间都应该尝试创建
    assert len(called["create_calls"]) == 3
    # 所有命名空间都应该授权（包括已存在的）
    assert len(called["grant_calls"]) == 3


@pytest.mark.asyncio
async def test_create_namespaces_and_grant_permissions_activity_with_errors(
    monkeypatch,
):
    """测试批量处理时遇到错误"""
    called = {"create_calls": [], "grant_calls": []}

    class FakeService:
        def create_namespace(self, cluster_id, namespace):
            called["create_calls"].append((cluster_id, namespace))
            if namespace == "ns2":
                raise Exception("创建失败")
            return True

        def grant_permission(self, cluster_id, namespace, ldap_user_name, role):
            called["grant_calls"].append((cluster_id, namespace, ldap_user_name, role))
            return True

    monkeypatch.setattr(
        kuboard_activities, "KuBoardService", lambda **kwargs: FakeService()
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

    params = KuboardNamespaceCreateParams(
        cluster_id="c1",
        namespaces=["ns1", "ns2", "ns3"],
        ldap_user_name="user",
        role="admin",
    )

    with pytest.raises(Exception, match="批量处理完成，成功: 2，失败: 1"):
        await kuboard_activities.create_namespaces_and_grant_permissions_activity(
            params
        )
