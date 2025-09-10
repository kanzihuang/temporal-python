#!/bin/bash

# 基础镜像 Docker 构建脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认镜像信息
BASE_IMAGE="temporal-python-base"
TAG="latest"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -h|--help)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  -t, --tag TAG     指定镜像标签 (默认: latest)"
            echo "  -h, --help        显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            echo "使用 -h 或 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🐳 开始构建基础镜像...${NC}"
echo -e "${YELLOW}🏷️  镜像标签: ${TAG}${NC}"

# 获取脚本所在目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo -e "${YELLOW}📁 项目根目录: ${PROJECT_ROOT}${NC}"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 构建基础镜像
echo -e "${BLUE}📦 构建基础镜像...${NC}"
docker build -t "${BASE_IMAGE}:${TAG}" -f "${SCRIPT_DIR}/base/Dockerfile" "${PROJECT_ROOT}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 基础镜像构建成功！${NC}"
    
    # 显示镜像信息
    echo -e "${BLUE}📋 镜像信息:${NC}"
    docker images "${BASE_IMAGE}"
    
    # 显示镜像大小
    IMAGE_SIZE=$(docker images --format "table {{.Size}}" "${BASE_IMAGE}:${TAG}" | tail -n 1)
    echo -e "${YELLOW}📏 镜像大小: ${IMAGE_SIZE}${NC}"
    
    echo -e "${GREEN}🚀 基础镜像构建完成！${NC}"
    echo -e "${YELLOW}现在可以构建其他工作流镜像:${NC}"
    echo -e "${YELLOW}./docker/build-kuboard.sh${NC}"
    echo -e "${YELLOW}./docker/build-vm.sh${NC}"
    
else
    echo -e "${RED}❌ 基础镜像构建失败！${NC}"
    exit 1
fi
