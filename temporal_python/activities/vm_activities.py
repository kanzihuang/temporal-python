import logging
from temporalio import activity
from temporalio.common import RetryPolicy
from temporal_python.services.vm_service import VMwareService
from temporal_python.shared.schemas import VMRequest
from temporal_python.shared.config import config

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(config.logging.level)

@activity.defn(name="create_vm_activity")
async def create_vm_activity(request: VMRequest) -> str:
    """Temporal活动：创建VMware虚拟机"""
    logger.info(f"开始创建虚拟机: {request.vm_name}")
    vmware_service = VMwareService()
    try:
        # 调用VMware服务创建虚拟机
        vm_name = vmware_service.create_vm(request)
        logger.info(f"虚拟机创建活动完成: {vm_name}")
        return vm_name
    except Exception as e:
        logger.error(f"虚拟机创建活动失败: {str(e)}", exc_info=True)
        # 抛出异常让Temporal处理重试
        raise Exception(f"创建虚拟机失败: {str(e)}") from e