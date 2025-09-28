import asyncio
import logging
from datetime import timedelta
from temporalio.worker import Worker
from temporalio.common import RetryPolicy
from src.workflows.kuboard_workflows import (
    KuboardNamespaceAuthorize,
    KuboardNamespaceCreate,
)
from src.activities.kuboard_activities import (
    create_namespace_activity,
    grant_permission_activity,
    create_namespaces_and_grant_permissions_activity,
)
from src.shared.config import get_temporal_client

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        logger.info("正在连接到 Temporal 服务器...")
        client = await get_temporal_client()
        logger.info("成功连接到 Temporal 服务器")

        logger.info("正在启动 kuboard worker...")
        worker = Worker(
            client,
            task_queue="kuboard",
            workflows=[KuboardNamespaceAuthorize, KuboardNamespaceCreate],
            activities=[
                create_namespace_activity,
                grant_permission_activity,
                create_namespaces_and_grant_permissions_activity,
            ],
            # 添加工作流任务级别的错误处理配置
            workflow_task_timeout=timedelta(seconds=60),
            workflow_task_retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=1,  # 关键：失败后不重试
                non_retryable_error_types=[
                    "RuntimeError",  # 捕获 Failed decoding arguments
                    "TypeError",  # 捕获 missing required positional argument
                    "ValueError",  # 捕获参数验证错误
                ],
            ),
        )

        logger.info("kuboard worker 已启动，正在监听任务队列: kuboard")
        logger.info("工作流任务配置：")
        logger.info("  - 任务超时：60秒")
        logger.info("  - 最大重试次数：1（失败后立即终止）")
        logger.info("  - 非重试错误类型：RuntimeError, TypeError, ValueError")
        logger.info("按 Ctrl+C 停止 worker...")
        await worker.run()

    except ConnectionError as e:
        logger.error(f"连接 Temporal 服务器失败: {e}")
        logger.error("请确保 Temporal 服务器正在运行")
        logger.error("可以使用以下命令启动 Temporal 开发服务器:")
        logger.error("  temporal server start-dev")
        logger.error("或者使用 Docker:")
        logger.error("  docker run --rm -p 7233:7233 temporalio/auto-setup:1.22.3")
        return 1
    except Exception as e:
        logger.error(f"启动 worker 时发生错误: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        if exit_code:
            exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Worker 已被用户中断")
    except Exception as e:
        logger.error(f"Worker 运行出错: {e}")
        exit(1)
