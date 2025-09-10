# Kuboard 工作流镜像
FROM temporal-python-base:latest

# 复制 Kuboard 相关代码
COPY temporal_python/activities/kuboard_activities.py ./temporal_python/activities/
COPY temporal_python/workflows/kuboard_workflows.py ./temporal_python/workflows/
COPY temporal_python/workers/kuboard_worker.py ./temporal_python/workers/

# 设置工作流特定环境变量
ENV WORKER_TYPE=kuboard
ENV TASK_QUEUE=kuboard

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import temporal_python.workers.kuboard_worker" || exit 1

# 启动命令
CMD ["poetry", "run", "python", "-m", "temporal_python.workers.kuboard_worker"]
