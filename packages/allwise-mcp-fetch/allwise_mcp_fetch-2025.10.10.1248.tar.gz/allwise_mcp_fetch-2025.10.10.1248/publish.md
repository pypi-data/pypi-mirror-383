# 发布指南

本指南说明如何发布 `allwise-mcp-fetch` 包到 PyPI。

## 快速开始

### 1. 获取API令牌

**TestPyPI（测试）：**
1. 访问 https://test.pypi.org/account/register/ 注册账户
2. 登录后进入 Account Settings → API tokens
3. 创建新令牌，复制令牌（格式：`pypi-xxxxxxxx`）

**PyPI（正式）：**
1. 访问 https://pypi.org/account/register/ 注册账户
2. 登录后进入 Account Settings → API tokens
3. 创建新令牌，复制令牌（格式：`pypi-xxxxxxxx`）

### 2. 设置环境变量

```bash
export TESTPYPI_TOKEN=pypi-你的TestPyPI令牌
export pypi-你的PyPI令牌
```

### 3. 发布包

```bash
# 发布到TestPyPI（测试）
./publish.sh --auto-version --test

# 发布到PyPI（正式）
./publish.sh --auto-version
```

## 脚本功能

### 基本用法

```bash
./publish.sh --help                    # 查看帮助
./publish.sh --build                   # 只构建包
./publish.sh --check                   # 只检查包
./publish.sh --clean                   # 清理构建文件
```

### 版本管理

```bash
./publish.sh --auto-version            # 自动生成版本号（基于日期）
./publish.sh --version 1.0.0           # 使用指定版本号
```

### 发布选项

```bash
./publish.sh --auto-version --test     # 发布到TestPyPI
./publish.sh --auto-version            # 发布到PyPI
./publish.sh --publish --test          # 只发布到TestPyPI
./publish.sh --publish                 # 只发布到PyPI
```

## 发布流程

1. **清理** - 删除之前的构建文件
2. **同步依赖** - 使用 `uv sync` 安装依赖
3. **构建** - 使用 `uv build` 构建包
4. **检查** - 使用 `twine check` 检查包质量
5. **发布** - 使用 `twine upload` 发布到PyPI

## 环境要求

- Python 3.10+
- uv 包管理器
- 有效的PyPI/TestPyPI账户和API令牌

## 故障排除

### 常见问题

1. **令牌错误**
   ```
   错误: 请设置 TESTPYPI_TOKEN 环境变量
   ```
   解决：确保已设置正确的环境变量

2. **构建失败**
   ```bash
   # 检查依赖
   uv sync --frozen --all-extras --dev
   ```

3. **发布失败**
   ```bash
   # 检查包质量
   uv run twine check dist/*
   ```

### 调试命令

```bash
# 详细构建信息
uv build --verbose

# 检查包内容
uv run twine check dist/* --verbose
```

## 安全提示

- 不要在代码中硬编码API令牌
- 使用环境变量存储敏感信息
- 定期轮换API令牌
- 在发布前仔细检查包内容

## 相关链接

- [PyPI](https://pypi.org)
- [TestPyPI](https://test.pypi.org)
- [uv文档](https://docs.astral.sh/uv/)
- [twine文档](https://twine.readthedocs.io/)