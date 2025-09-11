from pydantic import BaseModel, Field, validator
from typing import Optional
from pydantic import BaseModel, Field, validator

class VMRequest(BaseModel):
    vm_name: str = Field(..., min_length=1, max_length=80)
    guest_id: str = Field(default="otherGuest", description="VMware guest OS identifier")
    num_cpus: int = Field(..., gt=0, le=64)
    memory_gb: int = Field(..., gt=0, le=512)
    disk_size_gb: int = Field(..., gt=0, le=1024)
    power_on: bool = Field(default=True)
    notes: Optional[str] = Field(default=None, max_length=500)

    @validator('guest_id')
    def validate_guest_id(cls, v):
        valid_ids = ["otherGuest", "centos7_64Guest", "win2019srv_64Guest", "ubuntu64Guest"]
        if v not in valid_ids:
            raise ValueError(f"Invalid guest_id. Must be one of: {valid_ids}")
        return v

    class Config:
        extra = "forbid"  # 禁止未知字段
        json_schema_extra = {
            "example": {
                "vm_name": "test-vm-01",
                "guest_id": "ubuntu64Guest",
                "num_cpus": 2,
                "memory_gb": 4,
                "disk_size_gb": 40,
                "power_on": True,
                "notes": "Created via Temporal workflow"
            }
        }