#!/bin/bash

#    export TESTPYPI_TOKEN=pypi-你的TestPyPI令牌
#    export PYPI_TOKEN=pypi-你的PyPI令牌
#
#    ./publish.sh --auto-version --test    # 发布到TestPyPI
#    ./publish.sh --auto-version          # 发布到PyPI
#    ./publish.sh --build
#    ./publish.sh --help

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_directory() {
    if [ ! -f "pyproject.toml" ]; then
        print_error "请在包含 pyproject.toml 的目录中运行此脚本"
        exit 1
    fi
}

check_dependencies() {
    print_info "检查环境..."
    
    if ! command -v uv &> /dev/null; then
        print_error "uv 未安装，请先安装 uv:"
        print_error "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    print_info "同步依赖..."
    
    if ! uv sync --frozen --all-extras --dev; then
        print_error "依赖同步失败"
        exit 1
    fi
    
    print_info "环境准备完成"
}

get_current_version() {
    uv run python3 -c "
import tomlkit
with open('pyproject.toml') as f:
    data = tomlkit.parse(f.read())
    print(data['project']['version'])
"
}

generate_version() {
    date +"%Y.%m.%d.%H%M"
}

update_version() {
    local new_version=$1
    print_info "更新版本号为: $new_version"
    
    uv run python3 -c "
import tomlkit
with open('pyproject.toml') as f:
    data = tomlkit.parse(f.read())
    data['project']['version'] = '$new_version'

with open('pyproject.toml', 'w') as f:
    f.write(tomlkit.dumps(data))
"
}

clean_build() {
    print_info "清理构建文件..."
    rm -rf dist/ build/ *.egg-info/
    print_info "构建文件已清理"
}

build_package() {
    print_info "构建包..."
    if ! uv build; then
        print_error "构建失败"
        exit 1
    fi
    print_info "包构建成功"
}

check_package() {
    print_info "检查包..."
    
    # 检查 dist 目录
    if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
        print_error "没有找到构建的文件"
        exit 1
    fi
    
    print_info "找到构建文件: $(ls dist/)"
    
    # 使用 twine 检查包
    if ! uv run twine check dist/*; then
        print_error "包检查失败"
        exit 1
    fi
    print_info "包检查通过"
}

publish_to_pypi() {
    local test_mode=$1
    local repository
    local username="__token__"
    local password
    
    if [ "$test_mode" = "true" ]; then
        print_info "发布到 TestPyPI..."
        repository="https://test.pypi.org/legacy/"
        
        if [ -z "$TESTPYPI_TOKEN" ]; then
            print_error "请设置 TESTPYPI_TOKEN 环境变量"
            print_error "export TESTPYPI_TOKEN=pypi-你的TestPyPI令牌"
            exit 1
        fi
        password="$TESTPYPI_TOKEN"
    else
        print_info "发布到 PyPI..."
        repository="https://upload.pypi.org/legacy/"
        
        if [ -z "$PYPI_TOKEN" ]; then
            print_error "请设置 PYPI_TOKEN 环境变量"
            print_error "export PYPI_TOKEN=pypi-你的PyPI令牌"
            exit 1
        fi
        password="$PYPI_TOKEN"
    fi
    
    if ! uv run twine upload --username "$username" --password "$password" --repository-url "$repository" dist/*; then
        print_error "发布失败"
        exit 1
    fi
    
    print_info "包已成功发布到 $([ "$test_mode" = "true" ] && echo "TestPyPI" || echo "PyPI")"
}

show_help() {
    cat << EOF
发布脚本 for allwise-mcp-fetch 包

用法: $0 [选项]

选项:
    --version VERSION     指定版本号 (格式: x.y.z)
    --auto-version        自动生成版本号 (基于当前日期)
    --test                发布到 TestPyPI 而不是 PyPI
    --clean               只清理构建文件
    --build               只构建包
    --check               只检查包
    --publish             只发布包
    --help                显示此帮助信息

环境变量:
    TESTPYPI_TOKEN        TestPyPI API 令牌 (用于 --test)
    PYPI_TOKEN           PyPI API 令牌 (用于正式发布)

示例:
    # 设置环境变量
    export TESTPYPI_TOKEN=pypi-你的TestPyPI令牌
    export PYPI_TOKEN=pypi-你的PyPI令牌
    
    # 发布到 TestPyPI
    $0 --auto-version --test
    
    # 发布到 PyPI
    $0 --auto-version
    
    # 只构建包
    $0 --build

EOF
}

# 主函数
main() {
    local version=""
    local test_mode=false
    local clean_only=false
    local build_only=false
    local check_only=false
    local publish_only=false
    local auto_version=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                version="$2"
                shift 2
                ;;
            --auto-version)
                auto_version=true
                shift
                ;;
            --test)
                test_mode=true
                shift
                ;;
            --clean)
                clean_only=true
                shift
                ;;
            --build)
                build_only=true
                shift
                ;;
            --check)
                check_only=true
                shift
                ;;
            --publish)
                publish_only=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    check_directory
    
    check_dependencies
    
    if [ "$clean_only" = true ]; then
        clean_build
        return
    fi
    
    if [ -n "$version" ]; then
        print_info "使用指定版本: $version"
    elif [ "$auto_version" = true ]; then
        version=$(generate_version)
        print_info "自动生成版本: $version"
    else
        version=$(get_current_version)
        print_info "使用当前版本: $version"
    fi
    
    if [ -n "$version" ] && [ "$version" != "$(get_current_version)" ]; then
        update_version "$version"
    fi
    
    if [ "$build_only" = true ]; then
        clean_build
        build_package
        return
    fi
    
    if [ "$check_only" = true ]; then
        check_package
        return
    fi
    
    if [ "$publish_only" = true ]; then
        publish_to_pypi "$test_mode"
        return
    fi
    
    print_info "开始发布流程，版本: $version"
    
    clean_build
    
    build_package
    
    check_package
    
    local target="PyPI"
    [ "$test_mode" = true ] && target="TestPyPI"
    
    if read -p "确认发布到 $target? (y/N): " -r && [[ $REPLY =~ ^[Yy]$ ]]; then
        publish_to_pypi "$test_mode"
    else
        print_warning "发布已取消"
    fi
}

main "$@"
