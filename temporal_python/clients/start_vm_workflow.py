import asyncio
import logging
import argparse
import os
from temporalio.client import Client
from temporalio.common import WorkflowIDReusePolicy
from temporal_python.workflows.vm_workflows import VMCreationWorkflow
from temporal_python.shared.schemas import VMRequest
from temporal_python.shared.config import config
from datetime import timedelta

# 配置日志
logging.basicConfig(level=config.logging.level)
logger = logging.getLogger(__name__)

async def start_vm_workflow(request: VMRequest, temporal_host: str, temporal_port: int) -> str:
    """启动虚拟机创建工作流"""
    # 连接到Temporal服务
    client = await Client.connect(f"{temporal_host}:{temporal_port}")
    logger.info("成功连接到Temporal服务")

    # 启动工作流
    workflow_id = f"vm-creation-{request.vm_name}-{request.guest_id}-{request.num_cpus}-{request.memory_gb}-{request.disk_size_gb}"
    result = await client.execute_workflow(
            VMCreationWorkflow.run,
            request.model_dump(),
            id=workflow_id,
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE,
            task_queue="vmware",
            run_timeout=timedelta(minutes=60)
        )
    logger.info(f"VM creation workflow started with ID: {workflow_id}")
    print(f"Successfully started VM creation workflow. Workflow ID: {workflow_id}")
    return result

def main():
    """命令行入口：提交虚拟机创建请求"""
    parser = argparse.ArgumentParser(description="提交VMware虚拟机创建工作流到Temporal")
    parser.add_argument("--vm-name", required=True, help="虚拟机名称")
    parser.add_argument("--guest-id", default="otherGuest", help="VMware客户机OS标识符")
    parser.add_argument("--num-cpus", type=int, required=True, help="CPU数量")
    parser.add_argument("--memory-gb", type=int, required=True, help="内存大小(GB)")
    parser.add_argument("--disk-size-gb", type=int, required=True, help="磁盘大小(GB)")
    parser.add_argument("--power-on", action="store_true", default=True, help="创建后开机")
    parser.add_argument("--notes", help="虚拟机备注信息")
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

    args = parser.parse_args()

    # 创建VM请求对象
    try:
        vm_request = VMRequest(
            vm_name=args.vm_name,
            guest_id=args.guest_id,
            num_cpus=args.num_cpus,
            memory_gb=args.memory_gb,
            disk_size_gb=args.disk_size_gb,
            power_on=args.power_on,
            notes=args.notes
        )
    except Exception as e:
        logger.error(f"请求参数验证失败: {str(e)}")
        return

    # 启动工作流
    try:
        result = asyncio.run(start_vm_workflow(vm_request, args.temporal_host, args.temporal_port))
        logger.info(f"工作流执行成功，虚拟机名称: {result}")
    except Exception as e:
        logger.error(f"工作流启动失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()