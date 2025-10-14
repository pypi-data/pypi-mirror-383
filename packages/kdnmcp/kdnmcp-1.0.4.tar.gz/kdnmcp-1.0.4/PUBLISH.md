# 快递鸟MCP服务 PyPI发布指南

本文档详细说明如何将快递鸟MCP服务发布到PyPI。

## 准备工作

### 1. 环境准备

确保你的开发环境满足以下要求：

```bash
# Python版本
python --version  # 需要 >= 3.9

# 安装构建工具
pip install --upgrade pip setuptools wheel build twine hatchling
```

### 2. 账户准备

#### PyPI账户
1. 注册PyPI账户：https://pypi.org/account/register/
2. 启用两步验证（推荐）
3. 创建API Token：
   - 访问 https://pypi.org/manage/account/token/
   - 创建新的API token
   - 保存token（只显示一次）

#### TestPyPI账户（可选，用于测试）
1. 注册TestPyPI账户：https://test.pypi.org/account/register/
2. 创建API Token：https://test.pypi.org/manage/account/token/

### 3. 配置认证

#### 方法1：使用环境变量
```bash
# 设置环境变量
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-your-api-token-here
```

#### 方法2：使用.pypirc文件
在用户主目录创建 `.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## 发布流程

### 1. 更新版本号

在 `pyproject.toml` 中更新版本号：

```toml
[project]
name = "kdnmcp"
version = "1.0.1"  # 更新这里
```

版本号规则：
- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### 2. 更新项目信息

确保 `pyproject.toml` 中的信息正确：

```toml
[project]
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

[project.urls]
Homepage = "https://github.com/yourusername/kdnmcp"
Repository = "https://github.com/yourusername/kdnmcp.git"
```

### 3. 使用自动化脚本发布

#### 测试发布（推荐先测试）
```bash
python publish.py --test
```

#### 正式发布
```bash
python publish.py
```

#### 仅检查构建
```bash
python publish.py --check
```

### 4. 手动发布（可选）

如果不使用自动化脚本，可以手动执行：

```bash
# 1. 清理旧的构建文件
rmdir /s /q build dist *.egg-info 2>nul

# 2. 构建包
python -m build

# 3. 检查包
python -m twine check dist/*

# 4. 上传到测试PyPI（可选）
python -m twine upload --repository testpypi dist/*

# 5. 上传到正式PyPI
python -m twine upload dist/*
```

## 验证发布

### 1. 检查PyPI页面
访问 https://pypi.org/project/kdnmcp/ 确认包已成功上传。

### 2. 测试安装
```bash
# 创建新的虚拟环境测试
python -m venv test_env
test_env\Scripts\activate

# 安装包
pip install kdnmcp

# 测试命令
kdnmcp --help
```

### 3. 测试功能
```bash
# 创建测试配置
echo KDNIAO_EBUSINESS_ID=your_id > .env
echo KDNIAO_API_KEY=your_key >> .env

# 启动服务测试
kdnmcp --transport stdio
```

## 常见问题

### 1. 认证失败
```
HTTP Error 403: Invalid or non-existent authentication information
```

**解决方案：**
- 检查API token是否正确
- 确认用户名设置为 `__token__`
- 验证token权限范围

### 2. 包名冲突
```
HTTP Error 403: The user 'xxx' isn't allowed to upload to project 'xxx'
```

**解决方案：**
- 更改包名（在pyproject.toml中）
- 确认你有该包的上传权限

### 3. 版本冲突
```
HTTP Error 400: File already exists
```

**解决方案：**
- 更新版本号
- 不能重复上传相同版本

### 4. 构建失败
```
Error: Microsoft Visual C++ 14.0 is required
```

**解决方案：**
- 安装 Microsoft C++ Build Tools
- 或使用预编译的wheel包

## 最佳实践

### 1. 版本管理
- 使用语义化版本号
- 在git中打标签：`git tag v1.0.0`
- 保持CHANGELOG.md更新

### 2. 测试
- 先发布到TestPyPI测试
- 在不同环境中测试安装
- 验证所有功能正常

### 3. 文档
- 保持README.md更新
- 提供清晰的安装和使用说明
- 包含示例代码

### 4. 安全
- 不要在代码中硬编码API密钥
- 使用环境变量管理敏感信息
- 定期更新依赖包

## 自动化发布（GitHub Actions）

可以设置GitHub Actions自动发布：

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## 支持

如果在发布过程中遇到问题：

1. 查看PyPI官方文档：https://packaging.python.org/
2. 检查twine文档：https://twine.readthedocs.io/
3. 提交Issue到项目仓库

---

**注意：** 发布到PyPI是不可逆的操作，请确保在正式发布前充分测试。