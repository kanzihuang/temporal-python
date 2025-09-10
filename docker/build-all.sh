#!/bin/bash

# 多工作流 Docker 镜像构建脚本 - 通过调用各个单独的构建脚本实现
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认 TAG
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
            echo ""
            echo "示例:"
            echo "  $0                # 使用默认标签 latest"
            echo "  $0 -t v1.0.0     # 使用标签 v1.0.0"
            echo "  $0 --tag dev      # 使用标签 dev"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            echo "使用 -h 或 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🐳 开始构建多工作流 Docker 镜像...${NC}"
echo -e "${YELLOW}🏷️  镜像标签: ${TAG}${NC}"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 构建基础镜像
echo -e "${BLUE}📦 构建基础镜像...${NC}"
"${SCRIPT_DIR}/build-base.sh" -t "${TAG}"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 基础镜像构建失败！${NC}"
    exit 1
fi

# 构建 Kuboard 工作流镜像
echo -e "${BLUE}📦 构建 Kuboard 工作流镜像...${NC}"
"${SCRIPT_DIR}/build-kuboard.sh" -t "${TAG}"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Kuboard 工作流镜像构建失败！${NC}"
    exit 1
fi

# 构建 VM 工作流镜像
echo -e "${BLUE}📦 构建 VM 工作流镜像...${NC}"
"${SCRIPT_DIR}/build-vm.sh" -t "${TAG}"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ VM 工作流镜像构建失败！${NC}"
    exit 1
fi

# 显示所有镜像信息
echo -e "${BLUE}📋 所有镜像信息:${NC}"
docker images | grep temporal-python

echo -e "${GREEN}🎉 所有镜像构建完成！${NC}"
echo -e "${YELLOW}🚀 可以使用以下命令启动服务:${NC}"
echo -e "${YELLOW}docker-compose up -d${NC}"
echo -e "${YELLOW}或者单独启动某个工作流:${NC}"
echo -e "${YELLOW}docker-compose up -d kuboard-worker${NC}"
echo -e "${YELLOW}docker-compose up -d vm-worker${NC}"
