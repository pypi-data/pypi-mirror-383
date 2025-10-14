# 快速开始

5分钟内生成您的第一个PDF报告！

## 前提条件

确保已完成 [安装](./installation.md)。

## 方式一：最简单的示例

### 1. 创建Python脚本

创建文件 `my_first_report.py`：

```python
from pdf_generator import PDFReportGenerator

# 定义报告配置
config = {
    "metadata": {
        "title": "我的第一个PDF报告",
        "author": "张三"
    },
    "elements": [
        {
            "type": "text",
            "content": "欢迎使用PDF报告生成器！",
            "style": "Title"
        },
        {
            "type": "text",
            "content": "这是一个简单的示例报告，演示了如何快速生成PDF文档。",
            "style": "Normal"
        }
    ]
}

# 生成PDF
generator = PDFReportGenerator(config_dict=config)
generator.save("my_first_report.pdf")
print("✅ PDF报告已生成：my_first_report.pdf")
```

### 2. 运行脚本

```bash
python my_first_report.py
```

### 3. 查看结果

打开生成的 `my_first_report.pdf` 文件，您会看到一个包含标题和内容的PDF文档。

## 方式二：使用JSON配置文件

### 1. 创建配置文件

创建 `report_config.json`：

```json
{
  "metadata": {
    "title": "销售数据报告",
    "author": "数据分析部"
  },
  "elements": [
    {
      "type": "heading",
      "text": "2024年第一季度销售报告",
      "level": 1
    },
    {
      "type": "text",
      "content": "本报告总结了第一季度的销售业绩和市场趋势。",
      "style": "Normal"
    },
    {
      "type": "heading",
      "text": "销售概况",
      "level": 2
    },
    {
      "type": "text",
      "content": "- 总销售额：¥1,250,000\n- 同比增长：15%\n- 新客户数量：128",
      "style": "BodyText"
    }
  ]
}
```

### 2. 生成PDF

创建 `generate_from_json.py`：

```python
from pdf_generator import PDFReportGenerator

# 从JSON文件加载配置
generator = PDFReportGenerator(config_path="report_config.json")
generator.save("sales_report.pdf")
print("✅ 销售报告已生成！")
```

运行：

```bash
python generate_from_json.py
```

## 方式三：添加数据表格

### 1. 准备数据

创建 `sales_data.csv`：

```csv
产品名称,销量,销售额
智能手机,150,450000
平板电脑,80,240000
智能手表,200,200000
耳机,350,105000
```

### 2. 创建配置

创建 `table_report.json`：

```json
{
  "metadata": {
    "title": "产品销售明细"
  },
  "dataSources": [
    {
      "name": "sales",
      "type": "csv",
      "path": "sales_data.csv"
    }
  ],
  "elements": [
    {
      "type": "heading",
      "text": "产品销售统计表",
      "level": 1
    },
    {
      "type": "table",
      "dataSource": "sales",
      "style": {
        "gridColor": "#CCCCCC",
        "headerBackgroundColor": "#4472C4",
        "headerTextColor": "#FFFFFF",
        "alternateRowColor": "#F0F0F0"
      }
    }
  ]
}
```

### 3. 生成报告

```python
from pdf_generator import PDFReportGenerator

generator = PDFReportGenerator(config_path="table_report.json")
generator.save("product_sales.pdf")
print("✅ 产品销售报告已生成！")
```

## 方式四：添加图表

### 1. 创建包含图表的配置

创建 `chart_report.json`：

```json
{
  "metadata": {
    "title": "销售数据可视化"
  },
  "dataSources": [
    {
      "name": "sales",
      "type": "csv",
      "path": "sales_data.csv"
    }
  ],
  "elements": [
    {
      "type": "heading",
      "text": "产品销量图表",
      "level": 1
    },
    {
      "type": "chart",
      "chartType": "bar",
      "dataSource": "sales",
      "xColumn": "产品名称",
      "yColumn": "销量",
      "title": "各产品销量对比",
      "width": 400,
      "height": 300
    },
    {
      "type": "chart",
      "chartType": "pie",
      "dataSource": "sales",
      "labelColumn": "产品名称",
      "valueColumn": "销售额",
      "title": "销售额占比",
      "width": 400,
      "height": 300
    }
  ]
}
```

### 2. 生成图表报告

```python
from pdf_generator import PDFReportGenerator

generator = PDFReportGenerator(config_path="chart_report.json")
generator.save("chart_report.pdf")
print("✅ 图表报告已生成！")
```

## 方式五：使用Web API

### 1. 启动API服务

```bash
python run_api.py
```

### 2. 调用API生成PDF

使用Python requests：

```python
import requests
import json

# API配置
config = {
    "metadata": {"title": "API生成的报告"},
    "elements": [
        {
            "type": "text",
            "content": "这是通过API生成的PDF报告",
            "style": "Heading1"
        }
    ]
}

# 发送请求
response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json=config
)

# 保存PDF
with open("api_report.pdf", "wb") as f:
    f.write(response.content)

print("✅ API报告已生成！")
```

使用curl：

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"title": "测试报告"},
    "elements": [
      {"type": "text", "content": "Hello World", "style": "Normal"}
    ]
  }' \
  --output api_report.pdf
```

### 3. 查看API文档

访问：`http://localhost:8000/docs`

## 常用配置示例

### 添加图片

```json
{
  "elements": [
    {
      "type": "image",
      "path": "company_logo.png",
      "width": 200,
      "alignment": "center"
    }
  ]
}
```

### 添加分页符

```json
{
  "elements": [
    {
      "type": "text",
      "content": "第一页内容"
    },
    {
      "type": "pageBreak"
    },
    {
      "type": "text",
      "content": "第二页内容"
    }
  ]
}
```

### 使用模板变量

```json
{
  "metadata": {
    "title": "{{company}}月度报告",
    "author": "{{author_name}}"
  },
  "elements": [
    {
      "type": "text",
      "content": "报告日期：{{date}}"
    }
  ]
}
```

在Python中传递变量：

```python
config_parser.render_template(
    content,
    {"company": "ABC公司", "author_name": "李四", "date": "2024-03-15"}
)
```

## 运行项目示例

项目包含了完整的示例代码：

```bash
# 运行所有示例
python run_examples.py

# 查看生成的PDF
ls -l *.pdf
```

示例包括：
- `example_01_simple.pdf` - 简单文本报告
- `example_02_table.pdf` - 数据表格报告
- `example_03_charts.pdf` - 图表报告
- `example_04_comprehensive.pdf` - 综合完整报告

## 查看现有模板

项目提供了两个完整的模板：

### 1. 销售报告模板

```bash
# 使用销售报告模板
python -c "
from pdf_generator import PDFReportGenerator
gen = PDFReportGenerator(config_path='templates/sales_report.json')
gen.save('my_sales_report.pdf')
"
```

### 2. 财务报告模板

```bash
# 使用财务报告模板
python -c "
from pdf_generator import PDFReportGenerator
gen = PDFReportGenerator(config_path='templates/financial_report.json')
gen.save('my_financial_report.pdf')
"
```

## 下一步学习

现在您已经成功生成了第一个PDF报告！接下来可以：

1. **[创建完整报告](./first-report.md)** - 学习创建包含目录、页眉页脚的完整报告
2. **[理解基本概念](../02-user-guide/basic-concepts.md)** - 深入理解配置驱动和数据流
3. **[查看更多示例](../05-examples/simple-examples.md)** - 浏览丰富的示例代码
4. **[探索高级功能](../03-advanced-features/)** - 掌握页眉页脚、目录等高级特性

## 快速参考

### Python API 基础用法

```python
from pdf_generator import PDFReportGenerator

# 方式1：使用配置字典
generator = PDFReportGenerator(config_dict={...})

# 方式2：使用JSON文件
generator = PDFReportGenerator(config_path="config.json")

# 生成PDF文件
generator.save("output.pdf")

# 生成PDF字节流
pdf_bytes = generator.to_bytes()
```

### 配置文件基础结构

```json
{
  "metadata": {
    "title": "报告标题",
    "author": "作者姓名",
    "pageSize": "A4"
  },
  "dataSources": [...],
  "elements": [...]
}
```

## 获取帮助

- **文档首页**：[返回文档导航](../README.md)
- **完整用户手册**：[用户手册](../02-user-guide/)
- **API参考**：[API文档](../04-api-reference/)
- **常见问题**：[FAQ](../07-appendix/faq.md)

---

**上一页**：[安装指南](./installation.md)  
**下一页**：[创建第一个完整报告](./first-report.md)

