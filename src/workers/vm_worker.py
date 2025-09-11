import logging
import argparse
import asyncio
import os
from datetime import timedelta
from temporalio.client import Client


from temporalio.worker import Worker
from src.workflows.vm_workflows import VMCreationWorkflow
from src.activities.vm_activities import create_vm_activity
from src.shared.config import config

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
TEMPORAL_TASK_QUEUE = "vmware"

async def main(temporal_host: str, temporal_port: int):
    """启动Temporal Worker以处理VM创建工作流"""
    try:
        # 连接到Temporal服务
        logger.debug(f"尝试连接Temporal服务: {temporal_host}:{temporal_port}，超时时间10秒")
        # 设置连接超时为10秒
        try:
              logger.debug(f"开始连接Temporal服务: {temporal_host}:{temporal_port}，超时10秒")
              # 简化连接配置，使用默认传输层
              # 添加10秒连接超时控制
              client = await asyncio.wait_for(
                  Client.connect(f"{temporal_host}:{temporal_port}"),
                  timeout=10
              )
              logger.debug(f"✅ 成功连接到Temporal服务: {temporal_host}:{temporal_port}")
        except Exception as e:
            logger.error(f"连接Temporal服务失败: {str(e)}", exc_info=True)
            raise
        logger.debug("Temporal服务连接成功，客户端对象创建完成")
        logger.info("成功连接到Temporal服务")
        logger.debug("开始创建Worker实例")
        logger.debug(f"注册的工作流: {[w.__name__ for w in [VMCreationWorkflow]]}")
        logger.debug(f"注册的活动: {[a.__name__ for a in [create_vm_activity]]}")

        # 创建Worker并注册工作流和活动
        try:
            logger.debug("成功连接到Temporal服务，准备创建Worker")
            logger.debug("开始创建Worker实例并注册工作流和活动")
            async with Worker(
                client,
                task_queue=TEMPORAL_TASK_QUEUE,
                workflows=[VMCreationWorkflow],
                activities=[create_vm_activity]
            ):
                logger.info(f"Temporal Worker已启动，正在监听任务队列: {TEMPORAL_TASK_QUEUE}")
                logger.info("按Ctrl+C停止Worker...")
                # 保持Worker运行
                await asyncio.Future()
        except Exception as e:
            logger.error(f"Worker初始化失败: {str(e)}", exc_info=True)
            raise

    except Exception as e:
        logger.error(f"Worker启动失败: {str(e)}", exc_info=True)
        raise

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Temporal Worker for VMware VM creation workflow")
    parser.add_argument(
        "--temporal-host",
        default=os.getenv("TEMPORAL_HOST", "localhost"),
        help="Temporal server host address (default: localhost or TEMPORAL_HOST env var)"
    )
    parser.add_argument(
        "--temporal-port",
        type=int,
        default=int(os.getenv("TEMPORAL_PORT", "7233")),
        help="Temporal server port number (default: 7233 or TEMPORAL_PORT env var)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main(args.temporal_host, args.temporal_port))
    except KeyboardInterrupt:
        logger.info("Worker已被用户中断")
    except Exception as e:
        logger.error(f"Worker运行出错: {str(e)}", exc_info=True)