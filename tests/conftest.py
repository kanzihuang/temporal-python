"""
Pytest configuration and shared fixtures for temporal-python tests.
"""
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from temporal_python.shared.schemas import VMRequest
from temporal_python.shared.config import VMwareConfig, LoggingConfig, AppConfig


@pytest.fixture
def sample_vm_request():
    """提供标准的VM请求数据用于测试"""
    return VMRequest(
        vm_name="test-vm-01",
        guest_id="ubuntu64Guest",
        num_cpus=2,
        memory_gb=4,
        disk_size_gb=40,
        power_on=True,
        notes="Test VM created via unit test"
    )


@pytest.fixture
def sample_vmware_config():
    """提供VMware配置数据用于测试"""
    return VMwareConfig(
        host="test-vcenter.example.com",
        port=443,
        username="test-user@vsphere.local",
        password="test-password",
        datacenter="TestDatacenter",
        cluster="TestCluster",
        datastore="TestDatastore",
        network="TestNetwork",
        folder="/TestDatacenter/vm/TestFolder"
    )


@pytest.fixture
def sample_logging_config():
    """提供日志配置数据用于测试"""
    return LoggingConfig(
        level="INFO",
        file="test.log"
    )


@pytest.fixture
def sample_app_config(sample_vmware_config, sample_logging_config):
    """提供完整的应用配置数据用于测试"""
    return AppConfig(
        vmware=sample_vmware_config,
        logging=sample_logging_config
    )


@pytest.fixture
def temp_config_file(sample_app_config):
    """创建临时配置文件用于测试"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_app_config.dict(), f)
        yield f.name
    # 清理临时文件
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def mock_vmware_connection():
    """模拟VMware连接"""
    with patch('temporal_python.services.vmware_service.SmartConnect') as mock_connect:
        mock_connection = Mock()
        mock_content = Mock()
        mock_connection.RetrieveContent.return_value = mock_content
        mock_connect.return_value = mock_connection
        yield mock_connect, mock_connection, mock_content


@pytest.fixture
def mock_vim_objects():
    """模拟vSphere对象"""
    mock_datacenter = Mock()
    mock_datacenter.name = "TestDatacenter"
    
    mock_cluster = Mock()
    mock_cluster.name = "TestCluster"
    mock_cluster.resourcePool = Mock()
    
    mock_datastore = Mock()
    mock_datastore.name = "TestDatastore"
    
    mock_network = Mock()
    mock_network.name = "TestNetwork"
    
    mock_folder = Mock()
    mock_folder.name = "TestFolder"
    
    mock_vm = Mock()
    mock_vm.name = "test-vm-01"
    
    return {
        'datacenter': mock_datacenter,
        'cluster': mock_cluster,
        'datastore': mock_datastore,
        'network': mock_network,
        'folder': mock_folder,
        'vm': mock_vm
    }


@pytest.fixture
def mock_task():
    """模拟Temporal任务"""
    mock_task = Mock()
    mock_task.info.state = "success"
    mock_task.info.error = None
    return mock_task


@pytest.fixture
def mock_workflow_context():
    """模拟Temporal工作流上下文"""
    with patch('temporalio.workflow.execute_activity') as mock_execute:
        mock_execute.return_value = "test-vm-01"
        yield mock_execute 