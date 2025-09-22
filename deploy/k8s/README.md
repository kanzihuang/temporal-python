# Kubernetes 部署文件

本目录包含用于在 Kubernetes 集群上部署 kuboard worker 的 YAML 文件。

## 文件说明

- `kuboard-worker-config.yaml`: ConfigMap，包含 kuboard worker 的配置文件
- `kuboard-worker-deployment.yaml`: Deployment，定义 kuboard worker 的部署配置

## 部署步骤

1. 确保 Kubernetes 集群中已部署 Temporal 服务器（地址：temporal-frontend.temporal:7233）

2. 部署 ConfigMap：
```bash
kubectl apply -f kuboard-worker-config.yaml
```

3. 部署 kuboard worker：
```bash
kubectl apply -f kuboard-worker-deployment.yaml
```

## 配置说明

### ConfigMap 配置
- `kuboard.sites`: Kuboard 站点配置，包含访问 URL、用户名、访问密钥等
- `logging`: 日志配置，设置日志级别和输出文件

### Deployment 配置
- **镜像**: `eipwork/kuboard-worker:latest`
- **Temporal 连接**: 连接到 `temporal-frontend.temporal:7233`
- **任务队列**: `kuboard`
- **资源配置**: CPU 请求 100m，限制 500m；内存请求 128Mi，限制 512Mi

## 验证部署

检查 Pod 状态：
```bash
kubectl get pods -l app=kuboard-worker
```

查看日志：
```bash
kubectl logs -l app=kuboard-worker
```

## 注意事项

- kuboard worker 不对外提供服务，因此没有配置 Service
- 配置文件通过 ConfigMap 挂载到容器的 `/app/config/config.yaml` 路径
- 请根据实际环境调整 Temporal 服务器地址和 Kuboard 站点配置
