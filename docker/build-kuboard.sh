#!/bin/bash

# Kuboard Worker 镜像构建脚本
# 支持指定底包地址和版本

set -e

# 默认参数
BASE_IMAGE_REGISTRY=${BASE_IMAGE_REGISTRY:-"your-registry.com"}
BASE_IMAGE_NAME=${BASE_IMAGE_NAME:-"temporal-python-base"}
BASE_IMAGE_TAG=${BASE_IMAGE_TAG:-"latest"}
KUBOARD_IMAGE_REGISTRY=${KUBOARD_IMAGE_REGISTRY:-"your-registry.com"}
KUBOARD_IMAGE_NAME=${KUBOARD_IMAGE_NAME:-"kuboard-worker"}
KUBOARD_IMAGE_TAG=${KUBOARD_IMAGE_TAG:-"latest"}

# 显示构建参数
echo "=== Kuboard Worker 镜像构建参数 ==="
echo "底包镜像: ${BASE_IMAGE_REGISTRY}/${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}"
echo "目标镜像: ${KUBOARD_IMAGE_REGISTRY}/${KUBOARD_IMAGE_NAME}:${KUBOARD_IMAGE_TAG}"
echo "================================"

# 构建镜像
echo "开始构建 Kuboard Worker 镜像..."
docker build \
  --build-arg BASE_IMAGE_REGISTRY="${BASE_IMAGE_REGISTRY}" \
  --build-arg BASE_IMAGE_NAME="${BASE_IMAGE_NAME}" \
  --build-arg BASE_IMAGE_TAG="${BASE_IMAGE_TAG}" \
  -t "${KUBOARD_IMAGE_REGISTRY}/${KUBOARD_IMAGE_NAME}:${KUBOARD_IMAGE_TAG}" \
  -f docker/kuboard/Dockerfile \
  .

echo "镜像构建完成: ${KUBOARD_IMAGE_REGISTRY}/${KUBOARD_IMAGE_NAME}:${KUBOARD_IMAGE_TAG}"

# 可选：推送到镜像仓库
if [ "${PUSH_IMAGE}" = "true" ]; then
  echo "推送镜像到仓库..."
  docker push "${KUBOARD_IMAGE_REGISTRY}/${KUBOARD_IMAGE_NAME}:${KUBOARD_IMAGE_TAG}"
  echo "镜像推送完成"
fi