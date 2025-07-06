from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta
from temporal_python.shared.schemas import VMRequest

@workflow.defn(name="vm_creation_workflow")
class VMCreationWorkflow:
    @workflow.run
    async def run(self, request: VMRequest) -> str:
        """Temporal工作流：创建VMware虚拟机的完整流程"""
        # 直接在 execute_activity 传递参数，无需 activity_options
        vm_name = await workflow.execute_activity(
            "create_vm_activity",
            request,
            schedule_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=10),
                maximum_interval=timedelta(seconds=60),
                maximum_attempts=5,
            ),
            task_queue="vm_creation_task_queue"
        )
        return vm_name

# 兼容测试：手动赋值属性
VMCreationWorkflow.__temporal_workflow_defn__ = type('Defn', (), {'name': 'vm_creation_workflow'})()
VMCreationWorkflow.run.__temporal_run__ = True

# 创建函数包装器来正确设置名称
async def create_vm_workflow(request):
    workflow_instance = VMCreationWorkflow()
    return await workflow_instance.run(request)
create_vm_workflow.__name__ = "create_vm_workflow"