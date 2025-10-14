# 构建和发布指南

本文档说明如何构建和发布 `pdf-report-generator` 包到 PyPI。

## 准备工作

### 1. 安装构建工具

```bash
pip install build twine
```

### 2. 检查项目配置

确保以下文件已正确配置：
- `setup.py` - 包的元数据和依赖
- `pyproject.toml` - 现代化构建配置
- `MANIFEST.in` - 额外文件包含规则
- `LICENSE` - 许可证文件
- `README.md` - 项目说明

## 构建包

### 1. 清理旧构建

```bash
# Windows
rmdir /s /q build dist *.egg-info

# Linux/Mac
rm -rf build dist *.egg-info
```

### 2. 构建分发包

```bash
# 构建源码包和轮子包
python -m build

# 输出位置:
# - dist/pdf-report-generator-0.1.0.tar.gz (源码包)
# - dist/pdf_report_generator-0.1.0-py3-none-any.whl (轮子包)
```

### 3. 检查包内容

```bash
# 查看源码包内容
tar -tzf dist/pdf-report-generator-0.1.0.tar.gz

# 查看轮子包内容
unzip -l dist/pdf_report_generator-0.1.0-py3-none-any.whl
```

## 测试安装

### 在虚拟环境中测试

```bash
# 创建测试环境
python -m venv test_env

# 激活环境
# Windows
test_env\Scripts\activate
# Linux/Mac
source test_env/bin/activate

# 从本地安装
pip install dist/pdf_report_generator-0.1.0-py3-none-any.whl

# 测试导入
python -c "from pdf_generator import PDFReportGenerator; print('✅ 安装成功')"

# 运行完整测试
python test_installation.py

# 退出并删除测试环境
deactivate
# Windows
rmdir /s /q test_env
# Linux/Mac
rm -rf test_env
```

## 发布到 PyPI

### 1. 注册 PyPI 账号

- 测试服务器: https://test.pypi.org/account/register/
- 正式服务器: https://pypi.org/account/register/

### 2. 配置认证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token

[testpypi]
username = __token__
password = pypi-your-test-api-token
```

或使用环境变量：

```bash
# Windows
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-your-api-token

# Linux/Mac
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token
```

### 3. 上传到测试服务器

```bash
# 上传到 TestPyPI
python -m twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ pdf-report-generator
```

### 4. 上传到正式服务器

```bash
# 检查包
python -m twine check dist/*

# 上传到 PyPI
python -m twine upload dist/*
```

## 使用 GitHub Actions 自动发布

创建 `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

## 版本管理

### 更新版本号

需要同步更新以下文件中的版本号：

1. `setup.py` - line 8
2. `pyproject.toml` - line 7
3. `pdf_generator/__init__.py` - line 17
4. `api/__init__.py` - line 16

### 版本号规则

遵循语义化版本 (SemVer):
- `主版本.次版本.修订号`
- 例: `0.1.0` → `0.1.1` (修复) → `0.2.0` (新功能) → `1.0.0` (重大变更)

## 发布检查清单

在发布前确认：

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG 已更新
- [ ] 版本号已同步更新
- [ ] LICENSE 文件存在
- [ ] README.md 完整且准确
- [ ] 示例代码可运行
- [ ] 依赖版本已锁定
- [ ] 构建包已测试
- [ ] Git 标签已创建

## 本地开发安装

### 可编辑模式安装

```bash
# 基础安装
pip install -e .

# 包含 API
pip install -e .[api]

# 包含所有可选依赖
pip install -e .[all]
```

### 卸载

```bash
pip uninstall pdf-report-generator
```

## 常见问题

### Q: 上传失败 - "File already exists"

A: 版本号已存在，需要更新版本号后重新构建。

### Q: 导入失败

A: 检查包名 vs 导入名:
- 包名: `pdf-report-generator` (PyPI)
- 导入名: `pdf_generator` (Python)

### Q: 包含的文件不完整

A: 检查 `MANIFEST.in` 和 `setup.py` 中的 `package_data` 配置。

### Q: 依赖冲突

A: 使用版本范围而非固定版本，如 `>=4.0.0` 而非 `==4.0.7`。

## 有用的命令

```bash
# 检查包的元数据
python setup.py check

# 查看将要包含的文件
python setup.py sdist --dry-run

# 测试构建
python -m build --sdist --wheel --outdir dist/

# 验证包
twine check dist/*

# 查看已安装的包信息
pip show pdf-report-generator

# 查看包的文件
pip show -f pdf-report-generator
```

## 参考资料

- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)

