#!/bin/bash

# Git Hook测试和手动格式化脚本

set -e

COLORS=$(tput colors 2>/dev/null || echo '1')
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 颜色输出辅助函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🔧 Git Hook测试和维护工具"
echo "=============================="

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
    log_error "不在Git仓库中，请切换到项目根目录"
    exit 1
fi

# 检查poetry环境
if ! command -v poetry >/dev/null 2>&1; then
    log_error "未找到poetry命令，请确保已安装"
    exit 1
fi

log_info "📋 检查hooks权限和配置..."

# 检查pre-commit钩子
if [ -f ".git/hooks/pre-commit" ] && [ -x ".git/hooks/pre-commit" ]; then
    log_success "Pre-commit钩子已安装且可执行"
else
    log_error "Pre-commit钩子未安装或不可执行"
    exit 1
fi

# 检查pre-push钩子
if [ -f ".git/hooks/pre-push" ] && [ -x ".git/hooks/pre-push" ]; then
    log_success "Pre-push钩子已安装且可执行"
else
    log_error "Pre-push钩子未安装或不可执行"
    exit 1
fi

# 测试代码格式化
log_info "🔨 测试代码格式化..."

# 手动运行一次格式化测试
echo "格式化检查："
poetry run black --check src tests
if [ $? -eq 0 ]; then
    log_success "代码格式检查通过"
else
    log_warning "发现格式问题，正在自动修复..."
    poetry run black src tests
    log_success "格式已自动修复"
fi

echo ""
log_success "Git Hook配置完成！"
echo ""
echo "📚 使用方法："
echo "  git commit  : 自动检查和格式化代码"
echo "  git push    : 推送前完整代码质量检查"
echo "  manual     : poetry run black src tests"
echo ""

# 显示当前状态
log_info "当前git状态："
git status --short
