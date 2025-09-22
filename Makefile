# Temporal Python 多工作流 Docker 镜像构建 Makefile

# 默认配置
DOCKER_REGISTRY ?= 
IMAGE_PREFIX ?= temporal-python
TAG ?= latest

# 底包镜像配置
BASE_IMAGE_REGISTRY ?= $(DOCKER_REGISTRY)
BASE_IMAGE_NAME ?= $(IMAGE_PREFIX)-base
BASE_IMAGE_TAG ?= $(TAG)

# 镜像名称
LOCAL_BASE_IMAGE = $(IMAGE_PREFIX)-base
LOCAL_KUBOARD_IMAGE = $(IMAGE_PREFIX)-kuboard
LOCAL_VM_IMAGE = $(IMAGE_PREFIX)-vm

# 颜色定义
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# 默认目标
.PHONY: help
help: ## 显示帮助信息
	@echo "$(BLUE)🔧 Temporal Python Docker 镜像构建$(NC)"
	@echo ""
	@echo "$(YELLOW)用法:$(NC)"
	@echo "  make [目标] [变量=值]"
	@echo ""
	@echo "$(YELLOW)可用目标:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)可用变量:$(NC)"
	@echo "  $(GREEN)TAG$(NC)           镜像标签 (默认: latest)"
	@echo "  $(GREEN)IMAGE_PREFIX$(NC)  镜像前缀 (默认: temporal-python)"
	@echo "  $(GREEN)DOCKER_REGISTRY$(NC) Docker 仓库地址 (可选)"
	@echo "  $(GREEN)BASE_IMAGE_REGISTRY$(NC) 底包镜像仓库地址 (默认: DOCKER_REGISTRY)"
	@echo "  $(GREEN)BASE_IMAGE_NAME$(NC) 底包镜像名称 (默认: temporal-python-base)"
	@echo "  $(GREEN)BASE_IMAGE_TAG$(NC) 底包镜像标签 (默认: TAG)"
	@echo "  $(GREEN)LOCAL_BASE_IMAGE$(NC)   本地基础镜像名 (默认: $(IMAGE_PREFIX)-base)"
	@echo "  $(GREEN)LOCAL_KUBOARD_IMAGE$(NC) 本地 Kuboard 镜像名 (默认: $(IMAGE_PREFIX)-kuboard)"
	@echo "  $(GREEN)LOCAL_VM_IMAGE$(NC)      本地 VM 镜像名 (默认: $(IMAGE_PREFIX)-vm)"
	@echo ""
	@echo "$(YELLOW)示例:$(NC)"
	@echo "  make build-all                    # 构建所有镜像 (latest)"
	@echo "  make build-all TAG=v1.0.0        # 构建所有镜像 (v1.0.0)"
	@echo "  make build-kuboard TAG=dev        # 构建 Kuboard 镜像 (dev)"
	@echo "  make build-kuboard BASE_IMAGE_REGISTRY=your-registry.com BASE_IMAGE_TAG=v1.2.3"
	@echo "  make push-kuboard DOCKER_REGISTRY=your-registry.com TAG=v1.2.3"
	@echo "  make run-kuboard TAG=v1.2.3"
	@echo "  make push-all TAG=v1.0.0         # 推送所有镜像到仓库"

# 检查 Docker 是否运行
.PHONY: check-docker
check-docker:
	@if ! docker info > /dev/null 2>&1; then \
		echo "$(RED)❌ Docker 未运行，请先启动 Docker$(NC)"; \
		exit 1; \
	fi

# 构建基础镜像
.PHONY: build-base
build-base: check-docker ## 构建基础镜像
	@echo "$(BLUE)🔨 开始构建基础镜像...$(NC)"
	@echo "$(YELLOW)🏷️  镜像标签: $(TAG)$(NC)"
	@docker build -t $(LOCAL_BASE_IMAGE):$(TAG) -f docker/base/Dockerfile .
	@echo "$(GREEN)✅ 基础镜像构建成功！$(NC)"
	@docker images $(LOCAL_BASE_IMAGE)

# 构建 Kuboard 工作流镜像
.PHONY: build-kuboard
build-kuboard: check-docker ## 构建 Kuboard 工作流镜像
	@echo "$(BLUE)🔨 开始构建 Kuboard 工作流镜像...$(NC)"
	@echo "$(YELLOW)🏷️  镜像标签: $(TAG)$(NC)"
	@echo "$(YELLOW)📦 底包镜像: $(BASE_IMAGE_REGISTRY)/$(BASE_IMAGE_NAME):$(BASE_IMAGE_TAG)$(NC)"
	@if [ -n "$(BASE_IMAGE_REGISTRY)" ]; then \
		BASE_IMAGE_FULL=$(BASE_IMAGE_REGISTRY)/$(BASE_IMAGE_NAME):$(BASE_IMAGE_TAG); \
	else \
		BASE_IMAGE_FULL=$(BASE_IMAGE_NAME):$(BASE_IMAGE_TAG); \
	fi; \
	if ! docker images | grep -q "$$BASE_IMAGE_FULL"; then \
		echo "$(YELLOW)⚠️  底包镜像不存在: $$BASE_IMAGE_FULL$(NC)"; \
		echo "$(YELLOW)⚠️  请确保底包镜像已构建或从仓库拉取$(NC)"; \
		exit 1; \
	fi
	@docker build \
		--build-arg BASE_IMAGE_REGISTRY="$(BASE_IMAGE_REGISTRY)" \
		--build-arg BASE_IMAGE_NAME="$(BASE_IMAGE_NAME)" \
		--build-arg BASE_IMAGE_TAG="$(BASE_IMAGE_TAG)" \
		-t $(LOCAL_KUBOARD_IMAGE):$(TAG) \
		-f docker/kuboard/Dockerfile .
	@echo "$(GREEN)✅ Kuboard 工作流镜像构建成功！$(NC)"
	@docker images $(LOCAL_KUBOARD_IMAGE)

# 构建 VM 工作流镜像
.PHONY: build-vm
build-vm: check-docker ## 构建 VM 工作流镜像
	@echo "$(BLUE)🔨 开始构建 VM 工作流镜像...$(NC)"
	@echo "$(YELLOW)🏷️  镜像标签: $(TAG)$(NC)"
	@if ! docker images | grep -q "$(LOCAL_BASE_IMAGE)"; then \
		echo "$(YELLOW)⚠️  基础镜像不存在，先构建基础镜像...$(NC)"; \
		$(MAKE) build-base TAG=$(TAG); \
	fi
	@docker build -t $(LOCAL_VM_IMAGE):$(TAG) -f docker/vm/Dockerfile .
	@echo "$(GREEN)✅ VM 工作流镜像构建成功！$(NC)"
	@docker images $(LOCAL_VM_IMAGE)

# 构建所有镜像
.PHONY: build-all
build-all: build-base build-kuboard build-vm ## 构建所有镜像
	@echo "$(GREEN)🎉 所有镜像构建完成！$(NC)"
	@echo "$(BLUE)📋 所有镜像信息:$(NC)"
	@docker images | grep $(IMAGE_PREFIX)

# 清理本地镜像
.PHONY: clean
clean: ## 清理本地镜像
	@echo "$(YELLOW)🧹 清理本地镜像...$(NC)"
	@docker images | grep $(IMAGE_PREFIX) | awk '{print $$3}' | xargs -r docker rmi -f
	@echo "$(GREEN)✅ 清理完成！$(NC)"

# 清理指定标签的镜像
.PHONY: clean-tag
clean-tag: ## 清理指定标签的镜像
	@echo "$(YELLOW)🧹 清理标签为 $(TAG) 的镜像...$(NC)"
	@docker images | grep $(IMAGE_PREFIX) | grep $(TAG) | awk '{print $$3}' | xargs -r docker rmi -f
	@echo "$(GREEN)✅ 清理完成！$(NC)"

# 推送镜像到仓库
.PHONY: push-base
push-base: ## 推送基础镜像到仓库
	@if [ -z "$(DOCKER_REGISTRY)" ]; then \
		echo "$(RED)❌ 请设置 DOCKER_REGISTRY 变量$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📤 推送基础镜像到仓库...$(NC)"
	@docker tag $(LOCAL_BASE_IMAGE):$(TAG) $(DOCKER_REGISTRY)/$(LOCAL_BASE_IMAGE):$(TAG)
	@docker push $(DOCKER_REGISTRY)/$(LOCAL_BASE_IMAGE):$(TAG)
	@echo "$(GREEN)✅ 基础镜像推送成功！$(NC)"

.PHONY: push-kuboard
push-kuboard: ## 推送 Kuboard 镜像到仓库
	@if [ -z "$(DOCKER_REGISTRY)" ]; then \
		echo "$(RED)❌ 请设置 DOCKER_REGISTRY 变量$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📤 推送 Kuboard 镜像到仓库...$(NC)"
	@docker tag $(LOCAL_KUBOARD_IMAGE):$(TAG) $(DOCKER_REGISTRY)/$(LOCAL_KUBOARD_IMAGE):$(TAG)
	@docker push $(DOCKER_REGISTRY)/$(LOCAL_KUBOARD_IMAGE):$(TAG)
	@echo "$(GREEN)✅ Kuboard 镜像推送成功！$(NC)"

.PHONY: push-vm
push-vm: ## 推送 VM 镜像到仓库
	@if [ -z "$(DOCKER_REGISTRY)" ]; then \
		echo "$(RED)❌ 请设置 DOCKER_REGISTRY 变量$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📤 推送 VM 镜像到仓库...$(NC)"
	@docker tag $(LOCAL_VM_IMAGE):$(TAG) $(DOCKER_REGISTRY)/$(LOCAL_VM_IMAGE):$(TAG)
	@docker push $(DOCKER_REGISTRY)/$(LOCAL_VM_IMAGE):$(TAG)
	@echo "$(GREEN)✅ VM 镜像推送成功！$(NC)"

.PHONY: push-all
push-all: push-base push-kuboard push-vm ## 推送所有镜像到仓库
	@echo "$(GREEN)🎉 所有镜像推送完成！$(NC)"

# 运行容器
.PHONY: run-kuboard
run-kuboard: ## 运行 Kuboard 工作流容器
	@echo "$(BLUE)🚀 启动 Kuboard 工作流容器...$(NC)"
	@docker run -d --name kuboard-worker $(LOCAL_KUBOARD_IMAGE):$(TAG)

.PHONY: run-vm
run-vm: ## 运行 VM 工作流容器
	@echo "$(BLUE)🚀 启动 VM 工作流容器...$(NC)"
	@docker run -d --name vm-worker $(LOCAL_VM_IMAGE):$(TAG)

# 停止容器
.PHONY: stop-containers
stop-containers: ## 停止所有工作流容器
	@echo "$(YELLOW)⏹️  停止工作流容器...$(NC)"
	@docker stop kuboard-worker vm-worker 2>/dev/null || true
	@docker rm kuboard-worker vm-worker 2>/dev/null || true
	@echo "$(GREEN)✅ 容器已停止！$(NC)"

# 查看镜像信息
.PHONY: images
images: ## 查看所有相关镜像
	@echo "$(BLUE)📋 所有相关镜像:$(NC)"
	@docker images | grep $(IMAGE_PREFIX) || echo "没有找到相关镜像"

# 查看容器状态
.PHONY: ps
ps: ## 查看工作流容器状态
	@echo "$(BLUE)📊 工作流容器状态:$(NC)"
	@docker ps -a | grep -E "(kuboard-worker|vm-worker)" || echo "没有找到工作流容器"

# 开发环境快速构建
.PHONY: dev
dev: build-all TAG=dev ## 构建开发环境镜像
	@echo "$(GREEN)🎉 开发环境镜像构建完成！$(NC)"

# 生产环境构建
.PHONY: prod
prod: build-all TAG=latest ## 构建生产环境镜像
	@echo "$(GREEN)🎉 生产环境镜像构建完成！$(NC)"

# 使用构建脚本构建 Kuboard 镜像
.PHONY: build-kuboard-script
build-kuboard-script: ## 使用构建脚本构建 Kuboard 镜像
	@echo "$(BLUE)🔨 使用构建脚本构建 Kuboard 镜像...$(NC)"
	@BASE_IMAGE_REGISTRY=$(BASE_IMAGE_REGISTRY) \
	 BASE_IMAGE_NAME=$(BASE_IMAGE_NAME) \
	 BASE_IMAGE_TAG=$(BASE_IMAGE_TAG) \
	 KUBOARD_IMAGE_REGISTRY=$(DOCKER_REGISTRY) \
	 KUBOARD_IMAGE_NAME=$(LOCAL_KUBOARD_IMAGE) \
	 KUBOARD_IMAGE_TAG=$(TAG) \
	 ./docker/build-kuboard.sh
