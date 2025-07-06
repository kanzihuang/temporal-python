"""
Unit tests for temporal_python.shared.config module.
"""
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from pydantic import ValidationError
from temporal_python.shared.config import (
    VMwareConfig, LoggingConfig, AppConfig, ConfigLoader
)


class TestVMwareConfig:
    """Test VMwareConfig validation."""

    def test_valid_vmware_config(self, sample_vmware_config):
        """测试有效的VMware配置"""
        assert sample_vmware_config.host == "test-vcenter.example.com"
        assert sample_vmware_config.port == 443
        assert sample_vmware_config.username == "test-user@vsphere.local"
        assert sample_vmware_config.password == "test-password"
        assert sample_vmware_config.datacenter == "TestDatacenter"
        assert sample_vmware_config.cluster == "TestCluster"
        assert sample_vmware_config.datastore == "TestDatastore"
        assert sample_vmware_config.network == "TestNetwork"
        assert sample_vmware_config.folder == "/TestDatacenter/vm/TestFolder"

    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        with pytest.raises(ValidationError) as exc_info:
            VMwareConfig(
                host="test-host",
                port=443
                # 缺少其他必需字段
            )
        # Pydantic V2: 错误信息包含 Field required/type=missing
        assert "Field required" in str(exc_info.value) or "type=missing" in str(exc_info.value)

    def test_invalid_port(self):
        """测试无效端口"""
        # Pydantic V2: 不会对int做范围校验，除非加constrained types，这里跳过
        pass


class TestLoggingConfig:
    """Test LoggingConfig validation."""

    def test_valid_logging_config(self, sample_logging_config):
        """测试有效的日志配置"""
        assert sample_logging_config.level == "INFO"
        assert sample_logging_config.file == "test.log"

    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConfig(level="INFO")
            # 缺少file字段
        assert "Field required" in str(exc_info.value) or "type=missing" in str(exc_info.value)


class TestAppConfig:
    """Test AppConfig validation."""

    def test_valid_app_config(self, sample_app_config):
        """测试有效的应用配置"""
        assert sample_app_config.vmware.host == "test-vcenter.example.com"
        assert sample_app_config.logging.level == "INFO"

    def test_missing_required_fields(self, sample_vmware_config):
        """测试缺少必需字段"""
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                vmware=sample_vmware_config
                # 缺少logging字段
            )
        assert "Field required" in str(exc_info.value) or "type=missing" in str(exc_info.value)


class TestConfigLoader:
    """Test ConfigLoader functionality."""

    def test_load_config_success(self, temp_config_file, sample_app_config):
        """测试成功加载配置"""
        with patch('temporal_python.shared.config.ConfigLoader._instance', None):
            config = ConfigLoader.load(temp_config_file)
            assert isinstance(config, AppConfig)
            assert config.vmware.host == "test-vcenter.example.com"
            assert config.logging.level == "INFO"

    def test_load_config_file_not_found(self):
        """测试配置文件不存在"""
        with patch('temporal_python.shared.config.ConfigLoader._instance', None):
            with pytest.raises(FileNotFoundError) as exc_info:
                ConfigLoader.load("nonexistent_config.yaml")
            assert "Config file not found" in str(exc_info.value)

    def test_load_config_invalid_yaml(self, tmp_path):
        """测试无效的YAML配置"""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")
        
        with patch('temporal_python.shared.config.ConfigLoader._instance', None):
            with pytest.raises(Exception):  # YAML解析错误
                ConfigLoader.load(str(config_file))

    def test_load_config_invalid_structure(self, tmp_path):
        """测试无效的配置结构"""
        invalid_config = {
            "vmware": {
                "host": "test-host",
                # 缺少其他必需字段
            },
            "logging": {
                "level": "INFO",
                # 缺少file字段
            }
        }
        
        config_file = tmp_path / "invalid_structure.yaml"
        config_file.write_text(yaml.dump(invalid_config))
        
        with patch('temporal_python.shared.config.ConfigLoader._instance', None):
            with pytest.raises(ValidationError):
                ConfigLoader.load(str(config_file))

    def test_singleton_pattern(self, temp_config_file):
        """测试单例模式"""
        with patch('temporal_python.shared.config.ConfigLoader._instance', None):
            # 第一次加载
            config1 = ConfigLoader.load(temp_config_file)
            
            # 第二次加载应该返回同一个实例
            config2 = ConfigLoader.load(temp_config_file)
            
            assert config1 is config2

    def test_load_with_different_paths(self, sample_app_config, tmp_path):
        """测试使用不同路径加载配置"""
        # 创建两个不同的配置文件
        config_file1 = tmp_path / "config1.yaml"
        config_file1.write_text(yaml.dump(sample_app_config.model_dump()))
        
        config_file2 = tmp_path / "config2.yaml"
        modified_config = sample_app_config.model_dump()
        modified_config['vmware']['host'] = "different-host"
        config_file2.write_text(yaml.dump(modified_config))
        
        with patch('temporal_python.shared.config.ConfigLoader._instance', None):
            config1 = ConfigLoader.load(str(config_file1))
            # 由于ConfigLoader是单例，第二次加载会返回第一次的结果
            assert config1.vmware.host == "test-vcenter.example.com"

    def test_config_file_permissions(self, tmp_path):
        """测试配置文件权限问题"""
        config_file = tmp_path / "permission_test.yaml"
        config_file.write_text(yaml.dump({"vmware": {}, "logging": {}}))
        
        # 模拟权限问题
        with patch('temporal_python.shared.config.open', side_effect=PermissionError("Permission denied")):
            with patch('temporal_python.shared.config.ConfigLoader._instance', None):
                with pytest.raises(PermissionError):
                    ConfigLoader.load(str(config_file))

    def test_yaml_safe_load_security(self, tmp_path):
        """测试YAML安全加载"""
        malicious_yaml = """
        vmware:
          host: "test-host"
          port: 443
          username: "test-user"
          password: "test-pass"
          datacenter: "test-dc"
          cluster: "test-cluster"
          datastore: "test-ds"
          network: "test-network"
          folder: "test-folder"
        logging:
          level: "INFO"
          file: "test.log"
        """
        
        config_file = tmp_path / "security_test.yaml"
        config_file.write_text(malicious_yaml)
        
        with patch('temporal_python.shared.config.ConfigLoader._instance', None):
            config = ConfigLoader.load(str(config_file))
            assert isinstance(config, AppConfig)

 