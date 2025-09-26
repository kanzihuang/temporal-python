# Git Hooks 自动格式化配置

本项目配置了Git Hooks，可在提交时自动运行Black代码格式化。

## 🔧 配置概述

已安装的Git Hooks：
- **pre-commit**: 提交前自动格式化检查
- **pre-push**: 推送前完整代码质量检查

## 🚀 工作原理

### pre-commit Hook
- 每次 `git commit` 时自动触发
- 只检查提交中的Python文件
- 如格式有问题，自动修复并提示重新添加文件

### pre-push Hook
- 每次 `git push` 时自动触发
- 检查整个项目的代码格式
- 确保推送的代码符合Black标准

## 📋 使用方法

### 正常开发流程

```bash
# 1. 编辑代码
vim src/workflows/kuboard_workflows.py

# 2. 添加修改
git add src/workflows/kuboard_workflows.py

# 3. 提交（触发pre-commit hook）
git commit -m "修复xxx功能"
# -> 自动运行Black格式化检查
# -> 如果有格式问题，自动修复

# 4. 推送（触发pre-push hook）
git push origin main
# -> 完整项目代码质量检查
```

### 手动格式化

```bash
# 格式化所有代码
poetry run black src tests

# 检查格式（不修改）
poetry run black --check src tests
```

## ✨ 功能特性

### 智能检测
- 只检查修改的Python文件
- 自动跳过非Python文件
- 详细的格式对比提示

### 自动修复
- 发现格式问题时自动修复
- 提供修复后的下一步指引
- 清晰的错误提示和解决方案

### 分阶段检查
- **提交阶段**：检查并修复暂存文件
- **推送阶段**：完整项目质量检查

## 🛠️ Hook配置详情

### pre-commit行为
```bash
🎨 运行Pre-commit检查：格式化Python代码...
📝 检测到的Python文件:
  - src/workflows/kuboard_workflows.py
🔨 使用poetry运行Black格式化...
✅ 代码格式检查通过！
🎉 Pre-commit检查完成，可以安全提交！
```

### pre-push行为
```bash
🚀 运行Pre-push检查：代码质量验证...
📝 将要推送的Python文件:
  - src/workflows/kuboard_workflows.py
🔨 使用poetry进行完整代码格式检查...
✅ 所有代码格式检查通过！
🚀 Pre-push检查完成，代码质量验证通过！
```

## ⚠️ 故障排除

### Hook不工作？
```bash
# 检查权限
ls -la .git/hooks/pre*

# 修复权限
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### 跳过Hook（紧急情况）
```bash
# 跳过pre-commit hook
git commit --no-verify -m "紧急修复"

# 跳过pre-push hook
git push --no-verify
```

### 检查Hook内容
```bash
cat .git/hooks/pre-commit
cat .git/hooks/pre-push
```

## 📂 测试和维护

### 运行测试脚本
```bash
./scripts/format-hook-test.sh
```

### 手动测试格式化
```bash
# 修改一个Python文件，测试Hook
echo "# test" >> src/test.py
git add src/test.py
git commit -m "测试格式化"  # 触发pre-commit hook
```

## 🔍 日志和调试

### 查看详细输出
```bash
# 带详细信息的提交
git commit -v -m "提交描述"
```

### 查看Hook日志
```bash
# 在提交时查看具体执行过程
GIT_TRACE=1 git commit -m "测试"
```

## 🎯 团队协作

所有团队成员都需要运行时自动格式化，但Git Hook只在本地执行。

建议在项目中添加说明文档，提醒团队成员：
1. 确保编辑器中配置了Black格式化
2. 定期运行 `poetry run black src tests`
3. 遇到格式问题时查看此文档

## ✅ 完成状态

✅ Pre-commit hook 已安装  
✅ Pre-push hook 已安装  
✅ 所有Hook具有执行权限  
✅ 代码格式检查配置完成  
✅ 团队协作文档已完善
