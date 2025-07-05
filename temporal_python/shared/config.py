import yaml
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

class VMwareConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    datacenter: str
    cluster: str
    datastore: str
    network: str
    folder: str

class LoggingConfig(BaseModel):
    level: str
    file: str

class AppConfig(BaseModel):
    vmware: VMwareConfig
    logging: LoggingConfig

class ConfigLoader:
    _instance: Optional[AppConfig] = None

    @classmethod
    def load(cls, config_path: str = "config/config.yaml") -> AppConfig:
        if cls._instance is None:
            path = Path(config_path)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")

            with open(path, "r") as f:
                config_data = yaml.safe_load(f)

            cls._instance = AppConfig(**config_data)
        return cls._instance

# 全局配置实例
config = ConfigLoader.load()