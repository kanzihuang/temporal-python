# Docker 多工作流镜像构建

本目录包含了为不同工作流构建独立 Docker 镜像的配置和脚本。

## 📁 目录结构

```
docker/
├── base/                    # 基础镜像配置
│   └── Dockerfile          # 包含所有通用依赖的基础镜像
├── kuboard/                # Kuboard 工作流镜像配置
│   └── Dockerfile          # Kuboard 工作流专用镜像
├── vm/                     # VM 工作流镜像配置
│   └── Dockerfile          # VM 工作流专用镜像
├── build-all.sh           # 构建所有镜像的脚本 (调用各个单独脚本)
├── build-base.sh          # 仅构建基础镜像的脚本
├── build-kuboard.sh       # 仅构建 Kuboard 镜像的脚本
├── build-vm.sh            # 仅构建 VM 镜像的脚本
└── README.md              # 本文档
```

## 🐳 镜像说明

### 基础镜像 (temporal-python-base)
- 包含所有 Python 依赖和共享代码
- 作为其他工作流镜像的基础
- 包含 `temporal_python/shared/` 和 `temporal_python/services/`

### Kuboard 工作流镜像 (temporal-python-kuboard)
- 基于基础镜像构建
- 包含 Kuboard 相关的 activities、workflows 和 worker
- 专门用于处理 Kuboard 命名空间创建和授权任务

### VM 工作流镜像 (temporal-python-vm)
- 基于基础镜像构建
- 包含 VM 相关的 activities、workflows 和 worker
- 专门用于处理 VMware 虚拟机创建任务

## 🚀 使用方法

### 执行要求
- **Docker**: 需要 Docker 运行环境
- **执行目录**: 脚本可以从任何目录执行，会自动定位项目根目录
- **权限**: 脚本需要执行权限 (`chmod +x`)

### 镜像标签 (TAG)
所有构建脚本都支持通过 `-t` 或 `--tag` 参数指定镜像标签：

```bash
# 支持的标签格式
-t latest          # 默认标签
-t v1.0.0         # 版本标签
-t dev             # 开发环境标签
-t staging         # 测试环境标签
-t 20231201        # 日期标签
-t feature-abc     # 功能分支标签
```

**标签命名建议：**
- `latest`: 最新稳定版本
- `v1.0.0`: 语义化版本号
- `dev`: 开发版本
- `staging`: 测试版本
- `YYYYMMDD`: 日期版本

### 构建所有镜像
```bash
# 使用默认标签 latest
./docker/build-all.sh

# 指定自定义标签
./docker/build-all.sh -t v1.0.0
./docker/build-all.sh --tag dev

# 从任何目录执行
/path/to/temporal-python/docker/build-all.sh -t v1.0.0
```

### 构建单个镜像
```bash
# 使用默认标签 latest
./docker/build-base.sh
./docker/build-kuboard.sh
./docker/build-vm.sh

# 指定自定义标签
./docker/build-base.sh -t v1.0.0
./docker/build-kuboard.sh --tag dev
./docker/build-vm.sh -t staging

# 查看帮助信息
./docker/build-all.sh --help
./docker/build-kuboard.sh --help
```

### 使用 Docker Compose
```bash
# 启动所有服务
docker-compose up -d

# 仅启动 Kuboard 工作流
docker-compose up -d kuboard-worker

# 仅启动 VM 工作流
docker-compose up -d vm-worker
```

## ⚙️ 环境变量配置

### Kuboard 工作流
- `TEMPORAL_HOST`: Temporal 服务器地址
- `TEMPORAL_NAMESPACE`: Temporal 命名空间
- `TEMPORAL_TASK_QUEUE`: 任务队列名称 (kuboard)
- `KUBOARD_BASE_URL`: Kuboard 服务地址
- `KUBOARD_USERNAME`: Kuboard 用户名
- `KUBOARD_ACCESS_KEY`: Kuboard 访问密钥
- `KUBOARD_SECRET_KEY`: Kuboard 秘密密钥

### VM 工作流
- `TEMPORAL_HOST`: Temporal 服务器地址
- `TEMPORAL_NAMESPACE`: Temporal 命名空间
- `TEMPORAL_TASK_QUEUE`: 任务队列名称 (vm)
- `VMWARE_HOST`: VMware 服务器地址
- `VMWARE_USERNAME`: VMware 用户名
- `VMWARE_PASSWORD`: VMware 密码
- `VMWARE_DATACENTER`: VMware 数据中心

## 🔧 开发说明

### 添加新工作流
1. 在 `docker/` 目录下创建新的工作流目录
2. 创建对应的 `Dockerfile`
3. 在 `docker-compose.yml` 中添加新的服务配置
4. 创建对应的构建脚本

### 修改基础镜像
- 修改 `docker/base/Dockerfile`
- 重新构建基础镜像：`docker build -t temporal-python-base:latest -f docker/base/Dockerfile .`
- 所有依赖基础镜像的工作流镜像都需要重新构建

## 📋 镜像大小优化

- 使用多阶段构建减少镜像大小
- 使用 `.dockerignore` 排除不必要的文件
- 使用 Poetry 的 `--only=main` 选项只安装生产依赖
- 使用非 root 用户运行容器提高安全性

## 🏥 健康检查

每个工作流镜像都包含健康检查：
- 检查间隔：30秒
- 超时时间：10秒
- 重试次数：3次
- 启动等待时间：5-40秒

## 🔍 故障排除

### 构建失败
1. 检查 Docker 是否正在运行
2. 检查网络连接
3. 检查 Poetry 依赖是否正确安装
4. 查看构建日志中的具体错误信息

### 容器启动失败
1. 检查环境变量配置
2. 检查 Temporal 服务器是否可访问
3. 检查配置文件是否正确挂载
4. 查看容器日志：`docker logs <container_name>`
