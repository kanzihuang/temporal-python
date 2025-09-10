# 🐳 Docker 多工作流镜像设置完成

## ✅ 已完成的工作

### 1. 目录结构重组
```
docker/
├── base/                    # 基础镜像
│   └── Dockerfile          # 包含通用依赖
├── kuboard/                # Kuboard 工作流
│   └── Dockerfile          # Kuboard 专用镜像
├── vm/                     # VM 工作流
│   └── Dockerfile          # VM 专用镜像
├── build-all.sh           # 构建所有镜像
├── build-all.bat          # Windows 构建脚本
├── build-kuboard.sh       # 仅构建 Kuboard
├── build-vm.sh            # 仅构建 VM
└── README.md              # 详细文档
```

### 2. 镜像架构
- **基础镜像** (`temporal-python-base`): 包含所有 Python 依赖和共享代码
- **Kuboard 镜像** (`temporal-python-kuboard`): 专门处理 Kuboard 工作流
- **VM 镜像** (`temporal-python-vm`): 专门处理 VM 工作流

### 3. 构建脚本
- **全量构建**: `docker/build-all.sh` / `docker/build-all.bat`
- **单独构建**: `docker/build-kuboard.sh` / `docker/build-vm.sh`
- **自动依赖**: 自动检查并构建基础镜像

### 4. Docker Compose 配置
- 支持多服务编排
- 包含 Temporal 服务器、PostgreSQL、Web UI
- 独立的环境变量配置
- 健康检查和依赖管理

## 🚀 使用方法

### 构建所有镜像
```bash
# Linux/Mac
./docker/build-all.sh

# Windows
docker/build-all.bat
```

### 构建单个工作流
```bash
# 仅构建 Kuboard 工作流
./docker/build-kuboard.sh

# 仅构建 VM 工作流
./docker/build-vm.sh
```

### 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 仅启动 Kuboard 工作流
docker-compose up -d kuboard-worker

# 仅启动 VM 工作流
docker-compose up -d vm-worker
```

## 🔧 环境变量

### Kuboard 工作流
```bash
TEMPORAL_HOST=temporal-server:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=kuboard
KUBOARD_BASE_URL=http://kuboard.test.com:8089
KUBOARD_USERNAME=admin
KUBOARD_ACCESS_KEY=your_access_key
KUBOARD_SECRET_KEY=your_secret_key
```

### VM 工作流
```bash
TEMPORAL_HOST=temporal-server:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=vm
VMWARE_HOST=your_vmware_host
VMWARE_USERNAME=your_username
VMWARE_PASSWORD=your_password
VMWARE_DATACENTER=your_datacenter
```

## 📋 下一步

1. **构建镜像**: 运行构建脚本创建镜像
2. **配置环境**: 设置正确的环境变量
3. **启动服务**: 使用 docker-compose 启动服务
4. **测试工作流**: 验证工作流是否正常运行

## 🔍 故障排除

- 查看详细文档: `docker/README.md`
- 检查容器日志: `docker logs <container_name>`
- 验证环境变量: `docker exec <container_name> env`
- 检查健康状态: `docker ps`

## 🎯 优势

- **模块化**: 每个工作流独立镜像，便于维护
- **可扩展**: 易于添加新的工作流
- **高效**: 基础镜像共享，减少重复构建
- **安全**: 非 root 用户运行，健康检查
- **灵活**: 支持单独部署和全量部署
