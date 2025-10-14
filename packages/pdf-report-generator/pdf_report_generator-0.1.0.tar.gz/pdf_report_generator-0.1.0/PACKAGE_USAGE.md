# PDF Report Generator - 作为 Python 库使用

本文档说明如何将 `pdf-report-generator` 作为 Python 库安装和使用。

## 安装

### 1. 基础安装（仅 PDF 生成功能）

```bash
pip install pdf-report-generator
```

安装后可以使用：
- ✅ PDF 生成核心功能
- ✅ 所有数据源支持（CSV、JSON、Excel、数据库、API）
- ✅ 图表生成
- ✅ 模板引擎
- ❌ Web API 服务器（需要额外安装）

### 2. 包含 API 服务器

```bash
pip install pdf-report-generator[api]
```

安装后额外获得：
- ✅ FastAPI Web 服务器
- ✅ 命令行工具 `pdf-report-api`
- ✅ 程序化启动 API 的函数

### 3. 完整安装（包括开发工具）

```bash
pip install pdf-report-generator[all]
```

## 使用方式

### 1. 核心功能：生成 PDF

#### 基础使用

```python
from pdf_generator import PDFReportGenerator

# 简单配置
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
```

#### 使用数据源

```python
from pdf_generator import PDFReportGenerator
import pandas as pd

# 准备数据
data = pd.DataFrame({
    "产品": ["A", "B", "C"],
    "销量": [100, 200, 150]
})

# 配置
config = {
    "document": {"title": "销售报告"},
    "content": [
        {
            "type": "table",
            "dataSource": "sales"
        },
        {
            "type": "chart",
            "chartType": "bar",
            "dataSource": "sales",
            "options": {
                "x": "产品",
                "y": "销量"
            }
        }
    ]
}

# 生成
generator = PDFReportGenerator(config_dict=config)
generator.add_data_source("sales", data)
generator.generate("sales_report.pdf")
```

#### 生成字节流（不保存文件）

```python
from pdf_generator import PDFReportGenerator

generator = PDFReportGenerator(config_dict=config)
pdf_bytes = generator.to_bytes()

# 可以直接发送或存储
with open("output.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### 2. API 服务器

安装了 `pdf-report-generator[api]` 后，有三种方式启动 API 服务器：

#### 方式 A: Python 代码启动（推荐）

```python
from pdf_generator import start_api_server

# 启动服务器
start_api_server(
    host="localhost",
    port=8080,
    reload=True  # 开发模式
)
```

**参数说明：**
- `host`: 服务器地址，默认 `"0.0.0.0"`
- `port`: 端口号，默认 `8000`
- `reload`: 是否启用热重载（开发模式），默认 `False`
- `log_level`: 日志级别，默认 `"info"`
- `workers`: 工作进程数（生产环境），默认 `1`

**示例脚本：**

创建 `start_server.py`:

```python
from pdf_generator import start_api_server

if __name__ == "__main__":
    start_api_server(
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

运行:
```bash
python start_server.py
```

#### 方式 B: 命令行启动

```bash
# 默认配置 (0.0.0.0:8000)
pdf-report-api

# 自定义主机和端口
pdf-report-api --host localhost --port 8080

# 开发模式（热重载）
pdf-report-api --reload

# 生产模式（多进程）
pdf-report-api --workers 4

# 查看帮助
pdf-report-api --help
```

#### 方式 C: 获取 FastAPI 应用实例（高级）

如果需要自定义 FastAPI 应用：

```python
from pdf_generator import create_app
import uvicorn

# 获取应用
app = create_app()

# 添加自定义路由
@app.get("/custom/hello")
async def hello():
    return {"message": "Hello!"}

# 添加中间件
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 启动
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3. 访问 API

启动服务器后：

- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/health

**使用 API 生成 PDF:**

```python
import requests

config = {
    "document": {"title": "API 报告"},
    "content": [
        {"type": "text", "content": "从 API 生成"}
    ]
}

response = requests.post(
    "http://localhost:8000/api/generate",
    json={"config": config}
)

with open("api_report.pdf", "wb") as f:
    f.write(response.content)
```

## 导入说明

### 包名 vs 导入名

⚠️ **重要**: 包名和导入名不同！

- **安装时使用**: `pdf-report-generator`
  ```bash
  pip install pdf-report-generator
  ```

- **导入时使用**: `pdf_generator`
  ```python
  from pdf_generator import PDFReportGenerator
  ```

### 可用的导入

#### 基础安装后

```python
from pdf_generator import PDFReportGenerator
```

#### API 安装后

```python
from pdf_generator import (
    PDFReportGenerator,  # PDF 生成器
    start_api_server,    # 启动 API 服务器
    create_app           # 获取 FastAPI 应用
)
```

## 完整示例

### 示例 1: 简单报告

```python
from pdf_generator import PDFReportGenerator

config = {
    "document": {
        "title": "月度报告",
        "pageSize": "A4"
    },
    "content": [
        {
            "type": "text",
            "content": "2024年1月报告",
            "style": "Heading1"
        },
        {
            "type": "text",
            "content": "这是报告内容。",
            "style": "Normal"
        }
    ]
}

generator = PDFReportGenerator(config_dict=config)
generator.generate("monthly_report.pdf")
print("✅ 报告已生成")
```

### 示例 2: 数据驱动的报告

```python
from pdf_generator import PDFReportGenerator
import pandas as pd

# 数据
sales = pd.DataFrame({
    "月份": ["1月", "2月", "3月"],
    "销售额": [100000, 120000, 135000]
})

# 配置
config = {
    "document": {"title": "销售趋势"},
    "content": [
        {
            "type": "text",
            "content": "季度销售趋势",
            "style": "Heading1"
        },
        {
            "type": "chart",
            "chartType": "line",
            "dataSource": "sales",
            "options": {
                "x": "月份",
                "y": "销售额",
                "title": "销售趋势图"
            }
        },
        {
            "type": "table",
            "dataSource": "sales"
        }
    ]
}

# 生成
generator = PDFReportGenerator(config_dict=config)
generator.add_data_source("sales", sales)
generator.generate("sales_trend.pdf")
```

### 示例 3: 启动 API 服务器

```python
from pdf_generator import start_api_server

if __name__ == "__main__":
    print("🚀 启动 PDF Report API 服务器...")
    
    start_api_server(
        host="0.0.0.0",
        port=8080,
        reload=True,  # 开发模式
        log_level="info"
    )
```

### 示例 4: 自定义 API 应用

```python
from pdf_generator import create_app
import uvicorn

# 获取应用
app = create_app()

# 添加自定义端点
@app.get("/api/custom/status")
async def custom_status():
    return {
        "service": "PDF Generator",
        "status": "running",
        "custom": True
    }

# 添加自定义中间件
@app.middleware("http")
async def add_custom_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "PDF-Generator"
    return response

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
```

## 项目结构建议

### 作为库使用时的项目结构

```
your_project/
├── config/
│   └── report_template.json   # PDF 配置文件
├── data/
│   ├── sales.csv              # 数据文件
│   └── revenue.json
├── output/                    # 输出目录
├── generate_reports.py        # 生成脚本
└── start_api.py              # API 服务器启动脚本
```

**generate_reports.py:**
```python
from pdf_generator import PDFReportGenerator
import json

with open('config/report_template.json') as f:
    config = json.load(f)

generator = PDFReportGenerator(config_dict=config)
generator.generate('output/report.pdf')
```

**start_api.py:**
```python
from pdf_generator import start_api_server

if __name__ == "__main__":
    start_api_server(host="0.0.0.0", port=8000)
```

## 环境管理

### 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装库
pip install pdf-report-generator[api]

# 使用
python your_script.py

# 退出虚拟环境
deactivate
```

### requirements.txt

```
pdf-report-generator[api]==0.1.0
```

或分离可选依赖:

**requirements.txt:**
```
pdf-report-generator==0.1.0
```

**requirements-api.txt:**
```
pdf-report-generator[api]==0.1.0
```

## 验证安装

```bash
# 运行测试脚本
python test_installation.py

# 或手动测试
python -c "from pdf_generator import PDFReportGenerator; print('✅ 安装成功')"
```

## 常见问题

### Q: 导入失败 `ModuleNotFoundError: No module named 'pdf_generator'`

A: 确保已安装：
```bash
pip install pdf-report-generator
```

### Q: API 功能不可用

A: 需要安装 API 依赖：
```bash
pip install pdf-report-generator[api]
```

### Q: 命令 `pdf-report-api` 不存在

A: 
1. 确保安装了 `[api]` 依赖
2. 确保 Python Scripts 目录在 PATH 中
3. 可能需要重新打开终端

### Q: 中文显示问题

A: 
1. 将中文字体文件（如 SimHei.ttf、SimSun.ttf）放到项目的 `fonts/` 目录
2. 或指定字体目录：
   ```python
   generator = PDFReportGenerator(
       config_dict=config,
       font_dirs=['./fonts']
   )
   ```
3. 详细说明请参考 `FONT_CONFIGURATION.md`

## 下一步

- 📖 查看 [完整文档](docs/README.md)
- 🚀 运行 [示例代码](examples/library_usage_example.py)
- 📋 阅读 [快速入门](QUICKSTART.md)
- 🔧 查看 [API 文档](http://localhost:8000/docs)（启动服务器后）

## 更多资源

- [安装指南](INSTALLATION.md)
- [使用手册](USAGE_GUIDE.md)
- [构建发布指南](BUILD_PUBLISH.md)
- [GitHub 仓库](https://github.com/yourusername/pdf-report-generator)

