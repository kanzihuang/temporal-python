# Makefile 使用指南

## ✅ Makefile 已创建成功！

Makefile 已经创建在项目根目录，提供了比 shell 脚本更简洁的 Docker 镜像构建方式。

## ��� 使用方法

### 安装 make (如果未安装)
```bash
# Windows (使用 Chocolatey)
choco install make

# Windows (使用 Scoop)
scoop install make

# Ubuntu/Debian
sudo apt-get install make

# CentOS/RHEL
sudo yum install make
```

### 基本命令
```bash
# 查看帮助
make help

# 构建所有镜像
make build-all

# 构建指定标签的镜像
make build-all TAG=v1.0.0
make build-kuboard TAG=dev
make build-vm TAG=staging

# 查看镜像
make images

# 清理镜像
make clean
make clean-tag TAG=dev

# 运行容器
make run-kuboard
make run-vm
make stop-containers

# 推送镜像到仓库
make push-all DOCKER_REGISTRY=your-registry.com
```

## ��� 主要优势

### 1. 简洁性
- ✅ 一个文件替代 4 个 shell 脚本
- ✅ 标准化的构建流程
- ✅ 自动依赖管理

### 2. 功能丰富
- 智能依赖检查
- 并行构建支持
- 镜像清理功能
- 容器管理功能
- 镜像推送功能

### 3. 环境支持
```bash
make dev          # 开发环境 (TAG=dev)
make prod         # 生产环境 (TAG=latest)
```

## ��� 可用目标

| 目标 | 描述 |
|------|------|
| `help` | 显示帮助信息 |
| `build-base` | 构建基础镜像 |
| `build-kuboard` | 构建 Kuboard 工作流镜像 |
| `build-vm` | 构建 VM 工作流镜像 |
| `build-all` | 构建所有镜像 |
| `clean` | 清理所有镜像 |
| `clean-tag` | 清理指定标签的镜像 |
| `images` | 查看所有相关镜像 |
| `run-kuboard` | 运行 Kuboard 容器 |
| `run-vm` | 运行 VM 容器 |
| `stop-containers` | 停止所有容器 |
| `ps` | 查看容器状态 |
| `push-all` | 推送所有镜像到仓库 |
| `dev` | 构建开发环境镜像 |
| `prod` | 构建生产环境镜像 |

## ��� 可用变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `TAG` | `latest` | 镜像标签 |
| `IMAGE_PREFIX` | `temporal-python` | 镜像前缀 |
| `DOCKER_REGISTRY` | 空 | Docker 仓库地址 |

## ��� 示例

```bash
# 基本构建
make build-all

# 指定版本
make build-all TAG=v1.0.0

# 开发环境
make dev

# 生产环境
make prod

# 清理并重新构建
make clean && make build-all

# 推送到仓库
make push-all DOCKER_REGISTRY=registry.example.com
```

## ��� 迁移建议

1. **保留 shell 脚本**：作为备用方案
2. **逐步迁移**：先试用 Makefile
3. **最终清理**：确认 Makefile 工作正常后删除 shell 脚本

Makefile 提供了更标准化、更简洁的构建体验！
