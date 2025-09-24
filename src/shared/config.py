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
    # cluster_id 到 kuboard 站点名称的映射
    clusters: List[dict] = []

class LoggingConfig(BaseModel):
    level: str
    file: str

class AppConfig(BaseModel):
    vmware: Optional[VMwareConfig] = None
    kuboard: Optional[KuboardConfig] = None
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
        if not config.kuboard:
            raise ValueError("Kuboard configuration not found")

        for site in config.kuboard.sites:
            if site.name == site_name:
                return site
        raise ValueError(f"KuBoard site '{site_name}' not found in configuration")

    @classmethod
    def get_kuboard_site_by_cluster(cls, cluster_id: str) -> KuboardSiteConfig:
        """根据 cluster_id 获取映射的 KuBoard 站点配置。"""
        config = cls.load()
        if not config.kuboard or not getattr(config.kuboard, "clusters", None):
            raise ValueError(
                "No kuboard cluster mapping found in configuration. Please add 'kuboard.clusters' mapping and retry."
            )

        mapped_site_name: Optional[str] = None
        for item in config.kuboard.clusters:
            if isinstance(item, dict) and item.get("cluster_id") == cluster_id:
                mapped_site_name = item.get("kuboard_site_name")
                if mapped_site_name:
                    break

        if not mapped_site_name:
            raise ValueError(
                f"No kuboard_site_name mapping found for cluster_id '{cluster_id}'. Manual intervention required."
            )

        return cls.get_kuboard_site(mapped_site_name)

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
