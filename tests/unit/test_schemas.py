"""
Unit tests for temporal_python.shared.schemas module.
"""
import pytest
from pydantic import ValidationError
from temporal_python.shared.schemas import VMRequest


class TestVMRequest:
    """Test VMRequest schema validation and constraints."""

    def test_valid_vm_request(self, sample_vm_request):
        """测试有效的VM请求数据"""
        assert sample_vm_request.vm_name == "test-vm-01"
        assert sample_vm_request.guest_id == "ubuntu64Guest"
        assert sample_vm_request.num_cpus == 2
        assert sample_vm_request.memory_gb == 4
        assert sample_vm_request.disk_size_gb == 40
        assert sample_vm_request.power_on is True
        assert sample_vm_request.notes == "Test VM created via unit test"

    def test_vm_name_validation(self):
        """测试VM名称验证"""
        # 测试空名称
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="", num_cpus=2, memory_gb=4, disk_size_gb=40)
        assert "String should have at least 1 character" in str(exc_info.value)

        # 测试超长名称
        long_name = "a" * 81
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name=long_name, num_cpus=2, memory_gb=4, disk_size_gb=40)
        assert "String should have at most 80 characters" in str(exc_info.value)

    def test_guest_id_validation(self):
        """测试guest_id验证"""
        # 测试无效的guest_id
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(
                vm_name="test-vm",
                guest_id="invalid-guest",
                num_cpus=2,
                memory_gb=4,
                disk_size_gb=40
            )
        assert "Invalid guest_id" in str(exc_info.value)

        # 测试有效的guest_id
        valid_guests = ["otherGuest", "centos7_64Guest", "win2019srv_64Guest", "ubuntu64Guest"]
        for guest_id in valid_guests:
            vm_request = VMRequest(
                vm_name="test-vm",
                guest_id=guest_id,
                num_cpus=2,
                memory_gb=4,
                disk_size_gb=40
            )
            assert vm_request.guest_id == guest_id

    def test_cpu_validation(self):
        """测试CPU数量验证"""
        # 测试零CPU
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="test-vm", num_cpus=0, memory_gb=4, disk_size_gb=40)
        assert "Input should be greater than 0" in str(exc_info.value)

        # 测试负数CPU
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="test-vm", num_cpus=-1, memory_gb=4, disk_size_gb=40)
        assert "Input should be greater than 0" in str(exc_info.value)

        # 测试超过最大值的CPU
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="test-vm", num_cpus=65, memory_gb=4, disk_size_gb=40)
        assert "Input should be less than or equal to 64" in str(exc_info.value)

    def test_memory_validation(self):
        """测试内存大小验证"""
        # 测试零内存
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="test-vm", num_cpus=2, memory_gb=0, disk_size_gb=40)
        assert "Input should be greater than 0" in str(exc_info.value)

        # 测试超过最大值的内存
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="test-vm", num_cpus=2, memory_gb=513, disk_size_gb=40)
        assert "Input should be less than or equal to 512" in str(exc_info.value)

    def test_disk_size_validation(self):
        """测试磁盘大小验证"""
        # 测试零磁盘大小
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="test-vm", num_cpus=2, memory_gb=4, disk_size_gb=0)
        assert "Input should be greater than 0" in str(exc_info.value)

        # 测试超过最大值的磁盘大小
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(vm_name="test-vm", num_cpus=2, memory_gb=4, disk_size_gb=1025)
        assert "Input should be less than or equal to 1024" in str(exc_info.value)

    def test_notes_validation(self):
        """测试notes字段验证"""
        # 测试超长notes
        long_notes = "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(
                vm_name="test-vm",
                num_cpus=2,
                memory_gb=4,
                disk_size_gb=40,
                notes=long_notes
            )
        assert "String should have at most 500 characters" in str(exc_info.value)

        # 测试None notes（应该有效）
        vm_request = VMRequest(
            vm_name="test-vm",
            num_cpus=2,
            memory_gb=4,
            disk_size_gb=40,
            notes=None
        )
        assert vm_request.notes is None

    def test_default_values(self):
        """测试默认值"""
        vm_request = VMRequest(
            vm_name="test-vm",
            num_cpus=2,
            memory_gb=4,
            disk_size_gb=40
        )
        assert vm_request.guest_id == "otherGuest"
        assert vm_request.power_on is True
        assert vm_request.notes is None

    def test_extra_fields_forbidden(self):
        """测试禁止额外字段"""
        with pytest.raises(ValidationError) as exc_info:
            VMRequest(
                vm_name="test-vm",
                num_cpus=2,
                memory_gb=4,
                disk_size_gb=40,
                extra_field="should_fail"
            )
        assert "extra_field" in str(exc_info.value)

    def test_json_schema_extra(self):
        """测试JSON schema示例"""
        schema = VMRequest.schema()
        assert "example" in schema
        example = schema["example"]
        assert example["vm_name"] == "test-vm-01"
        assert example["guest_id"] == "ubuntu64Guest"
        assert example["num_cpus"] == 2
        assert example["memory_gb"] == 4
        assert example["disk_size_gb"] == 40
        assert example["power_on"] is True
        assert example["notes"] == "Created via Temporal workflow" 