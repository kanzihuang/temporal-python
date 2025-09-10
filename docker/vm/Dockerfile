# VM 工作流镜像
FROM temporal-python-base:latest

# 复制 VM 相关代码
COPY temporal_python/activities/vm_activities.py ./temporal_python/activities/
COPY temporal_python/workflows/vm_workflows.py ./temporal_python/workflows/
COPY temporal_python/workers/vm_worker.py ./temporal_python/workers/
COPY temporal_python/clients/start_vm_workflow.py ./temporal_python/clients/

# 设置工作流特定环境变量
ENV WORKER_TYPE=vm
ENV TASK_QUEUE=vm

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import temporal_python.workers.vm_worker" || exit 1

# 启动命令
CMD ["poetry", "run", "python", "-m", "temporal_python.workers.vm_worker"]
