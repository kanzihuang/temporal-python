# Kuboard 工作流镜像
# 支持通过构建参数指定底包地址和版本
ARG BASE_IMAGE_REGISTRY=your-registry.com
ARG BASE_IMAGE_NAME=temporal-python-base
ARG BASE_IMAGE_TAG=latest
FROM ${BASE_IMAGE_REGISTRY}/${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}

# 复制共享代码
COPY src/shared/ ./src/shared/

# 复制 Kuboard 相关代码
COPY src/services/kuboard_service.py ./src/services/
COPY src/activities/kuboard_activities.py ./src/activities/
COPY src/workflows/kuboard_workflows.py ./src/workflows/
COPY src/workers/kuboard_worker.py ./src/workers/

# 设置工作流特定环境变量
ENV WORKER_TYPE=kuboard
ENV TASK_QUEUE=kuboard

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import temporal_python.workers.kuboard_worker" || exit 1

# 启动命令
CMD ["poetry", "run", "python", "-m", "temporal_python.workers.kuboard_worker"]
