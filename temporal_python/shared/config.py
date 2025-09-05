import yaml
import os
import asyncio
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
from temporalio.client import Client

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

class KuboardSiteConfig(BaseModel):
    name: str
    url: str
    username: str
    access_key: str
    secret_key: str

class KuboardConfig(BaseModel):
    sites: List[KuboardSiteConfig]

class LoggingConfig(BaseModel):
    level: str
    file: str

class AppConfig(BaseModel):
    vmware: VMwareConfig
    kuboard: KuboardConfig
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

    @classmethod
    def get_kuboard_site(cls, site_name: str) -> KuboardSiteConfig:
        """根据站点名称获取 KuBoard 配置"""
        config = cls.load()
        for site in config.kuboard.sites:
            if site.name == site_name:
                return site
        raise ValueError(f"KuBoard site '{site_name}' not found in configuration")

async def get_temporal_client() -> Client:
    """获取 Temporal 客户端连接"""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost")
    temporal_port = int(os.getenv("TEMPORAL_PORT", "7233"))

    try:
        client = await asyncio.wait_for(
            Client.connect(f"{temporal_host}:{temporal_port}"),
            timeout=10
        )
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Temporal server at {temporal_host}:{temporal_port}: {str(e)}")

# 全局配置实例
config = ConfigLoader.load()