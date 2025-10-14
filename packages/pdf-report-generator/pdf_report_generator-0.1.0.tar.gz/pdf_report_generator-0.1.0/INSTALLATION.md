# PDF Report Generator - 安装指南

## 安装方式

### 方式 1: 从 PyPI 安装（推荐，发布后）

```bash
# 基础安装（仅核心功能）
pip install pdf-report-generator

# 安装包含 API 服务器
pip install pdf-report-generator[api]

# 安装所有功能（包括开发工具）
pip install pdf-report-generator[all]
```

### 方式 2: 从源码安装（开发环境）

```bash
# 克隆仓库
git clone https://github.com/yourusername/pdf-report-generator.git
cd pdf-report-generator

# 安装为可编辑模式
pip install -e .

# 或安装包含 API 支持
pip install -e .[api]

# 或安装所有依赖
pip install -e .[all]
```

### 方式 3: 使用 requirements.txt

```bash
# 克隆仓库后
cd pdf-report-generator
pip install -r requirements.txt
```

## 验证安装

### 测试核心功能

```python
from pdf_generator import PDFReportGenerator

print("✅ PDF Report Generator 安装成功！")
print(f"版本: {PDFReportGenerator.__module__}")
```

### 测试 API 服务器

```bash
# 使用命令行启动
pdf-report-api --help

# 或使用 Python
python -c "from pdf_generator import start_api_server; print('✅ API 服务器可用')"
```

## 快速开始

### 1. 基础使用（生成 PDF）

```python
from pdf_generator import PDFReportGenerator

# 配置
config = {
    "document": {
        "title": "示例报告",
        "pageSize": "A4"
    },
    "content": [
        {
            "type": "text",
            "content": "Hello, PDF!",
            "style": "Heading1"
        }
    ]
}

# 生成 PDF
generator = PDFReportGenerator(config_dict=config)
generator.generate("output.pdf")
print("✅ PDF 已生成: output.pdf")
```

### 2. 启动 API 服务器

#### 方式 A: 使用 Python 代码

```python
from pdf_generator import start_api_server

# 启动服务器
start_api_server(
    host="localhost",
    port=8080,
    reload=True  # 开发模式
)
```

#### 方式 B: 使用命令行

```bash
# 默认配置（0.0.0.0:8000）
pdf-report-api

# 自定义主机和端口
pdf-report-api --host localhost --port 8080

# 开发模式（热重载）
pdf-report-api --reload

# 生产模式（多进程）
pdf-report-api --workers 4
```

#### 方式 C: 使用启动脚本

创建 `start_server.py`:

```python
from pdf_generator import start_api_server

if __name__ == "__main__":
    start_api_server(
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4
    )
```

然后运行:

```bash
python start_server.py
```

### 3. 访问 API 文档

启动服务器后，访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API Root: http://localhost:8000/

## 依赖说明

### 核心依赖（必需）

- reportlab >= 4.0.0 - PDF 生成引擎
- Pillow >= 10.0.0 - 图像处理
- pandas >= 2.0.0 - 数据处理
- matplotlib >= 3.7.0 - 图表生成
- Jinja2 >= 3.0.0 - 模板引擎
- openpyxl >= 3.0.0 - Excel 支持
- requests >= 2.28.0 - HTTP 请求
- SQLAlchemy >= 2.0.0 - 数据库支持

### API 依赖（可选）

- fastapi >= 0.100.0 - Web 框架
- uvicorn[standard] >= 0.23.0 - ASGI 服务器
- python-multipart >= 0.0.6 - 文件上传
- pydantic >= 2.0.0 - 数据验证

### 开发依赖（可选）

- pytest >= 7.0.0 - 测试框架
- black >= 23.0.0 - 代码格式化
- flake8 >= 6.0.0 - 代码检查

## 常见问题

### Q: 如何只安装核心功能？

```bash
pip install pdf-report-generator
```

这将只安装 PDF 生成相关的依赖，不包括 API 服务器。

### Q: 安装后无法导入？

确保使用正确的包名：

```python
# ✅ 正确
from pdf_generator import PDFReportGenerator

# ❌ 错误
from pdf_report_generator import PDFReportGenerator
```

### Q: API 服务器无法启动？

确保安装了 API 依赖：

```bash
pip install pdf-report-generator[api]
```

### Q: 中文字体问题？

PDF Report Generator **不包含字体文件**，需要用户自己提供。

**快速解决：**

1. 在项目目录创建 `fonts/` 文件夹
2. 将中文字体文件（如 SimHei.ttf、SimSun.ttf）放入该文件夹
3. 系统会自动检测并使用

**详细配置：**
- 参考 `FONT_CONFIGURATION.md` - 完整字体配置指南
- 参考 `docs/03-advanced-features/chinese-fonts.md` - 中文字体详细说明

## 卸载

```bash
pip uninstall pdf-report-generator
```

## 下一步

- 查看 [快速入门](QUICKSTART.md)
- 阅读 [使用指南](USAGE_GUIDE.md)
- 浏览 [完整文档](docs/README.md)
- 查看 [示例代码](examples/)

