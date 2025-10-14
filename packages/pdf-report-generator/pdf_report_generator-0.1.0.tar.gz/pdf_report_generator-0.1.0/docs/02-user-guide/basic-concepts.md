# 基本概念

理解PDF报告生成器的核心概念将帮助您更好地使用和定制系统。

## 配置驱动架构

### 什么是配置驱动？

PDF报告生成器采用**配置驱动**的设计理念。这意味着：

- ✅ **无需编写复杂代码**：通过JSON配置文件定义报告结构
- ✅ **声明式设计**：描述"要什么"而不是"怎么做"
- ✅ **灵活可复用**：配置可以保存、共享和重用
- ✅ **易于维护**：修改配置即可调整报告，无需改动代码

### 配置文件结构

一个典型的配置文件包含三个主要部分：

```json
{
  "metadata": {
    "title": "报告标题",
    "author": "作者"
  },
  "dataSources": [
    {
      "name": "销售数据",
      "type": "csv",
      "path": "sales.csv"
    }
  ],
  "elements": [
    {
      "type": "text",
      "content": "报告内容"
    }
  ]
}
```

## 核心组件

### 1. 元数据（Metadata）

元数据定义了报告的基本信息：

```json
{
  "metadata": {
    "title": "销售报告",        // PDF标题
    "author": "张三",            // 作者
    "subject": "月度销售分析",   // 主题
    "keywords": "销售,分析",     // 关键词
    "pageSize": "A4",           // 页面大小
    "orientation": "portrait"   // 页面方向
  }
}
```

**可用的页面尺寸**：
- `A4`（默认）：210 × 297 mm
- `A3`：297 × 420 mm
- `A5`：148 × 210 mm
- `LETTER`：8.5 × 11 英寸
- `LEGAL`：8.5 × 14 英寸

**页面方向**：
- `portrait`：纵向（默认）
- `landscape`：横向

### 2. 数据源（Data Sources）

数据源是报告数据的来源。系统支持多种数据源类型：

#### CSV文件

```json
{
  "dataSources": [
    {
      "name": "sales",
      "type": "csv",
      "path": "data/sales.csv",
      "encoding": "utf-8"
    }
  ]
}
```

#### JSON文件

```json
{
  "dataSources": [
    {
      "name": "products",
      "type": "json",
      "path": "data/products.json",
      "jsonPath": "$.products"  // JSON路径（可选）
    }
  ]
}
```

#### Excel文件

```json
{
  "dataSources": [
    {
      "name": "budget",
      "type": "excel",
      "path": "data/budget.xlsx",
      "sheet": "Sheet1"  // 工作表名称（可选）
    }
  ]
}
```

#### HTTP API

```json
{
  "dataSources": [
    {
      "name": "api_data",
      "type": "api",
      "url": "https://api.example.com/sales",
      "method": "GET",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  ]
}
```

#### 数据库

```json
{
  "dataSources": [
    {
      "name": "db_sales",
      "type": "database",
      "connection": "sqlite:///sales.db",
      "query": "SELECT * FROM sales WHERE year = 2024"
    }
  ]
}
```

#### 内联数据

```json
{
  "dataSources": [
    {
      "name": "inline_data",
      "type": "inline",
      "data": [
        {"name": "产品A", "sales": 1000},
        {"name": "产品B", "sales": 1500}
      ]
    }
  ]
}
```

### 3. 元素（Elements）

元素是PDF报告的构建块。每个元素代表报告中的一个组件。

#### 文本元素

```json
{
  "type": "text",
  "content": "这是一段文本",
  "style": "Normal"
}
```

#### 标题元素

```json
{
  "type": "heading",
  "text": "第一章",
  "level": 1  // 1-6级标题
}
```

#### 表格元素

```json
{
  "type": "table",
  "dataSource": "sales",
  "columns": ["产品", "销量", "金额"],
  "style": {...}
}
```

#### 图表元素

```json
{
  "type": "chart",
  "chartType": "bar",
  "dataSource": "sales",
  "xColumn": "月份",
  "yColumn": "销售额"
}
```

#### 图片元素

```json
{
  "type": "image",
  "path": "logo.png",
  "width": 200,
  "alignment": "center"
}
```

#### 其他元素

```json
// 分页符
{"type": "pageBreak"}

// 空白间隔
{"type": "spacer", "height": 20}

// 列表
{"type": "list", "items": ["项目1", "项目2"]}
```

## 数据流程

### 1. 配置加载

```
配置文件(JSON) → 配置解析器 → 验证 → 内部配置对象
```

### 2. 数据获取

```
数据源配置 → 数据源加载器 → 原始数据 → Pandas DataFrame
```

### 3. 元素生成

```
元素配置 → 元素工厂 → ReportLab Flowable → PDF文档
```

### 4. PDF构建

```
所有元素 → 文档模板 → 布局引擎 → 最终PDF
```

## 模板变量系统

### 什么是模板变量？

模板变量允许在配置中使用动态内容，使用Jinja2模板语法。

### 基本语法

```json
{
  "elements": [
    {
      "type": "text",
      "content": "报告日期：{{date}}"
    },
    {
      "type": "text",
      "content": "作者：{{metadata.author}}"
    }
  ]
}
```

### 内置变量

系统提供以下内置变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{date}}` | 当前日期 | 2024-03-15 |
| `{{datetime}}` | 当前日期时间 | 2024-03-15 14:30 |
| `{{year}}` | 当前年份 | 2024 |
| `{{page}}` | 当前页码 | 3 |
| `{{total}}` | 总页数 | 10 |
| `{{metadata.xxx}}` | 元数据字段 | 报告标题 |

### 数据源变量

可以访问数据源中的数据：

```json
{
  "type": "text",
  "content": "总销售额：{{dataSources.sales.sales.sum()}}"
}
```

### 条件和循环

```json
{
  "type": "text",
  "content": "{% if metadata.urgent %}【紧急】{% endif %}{{metadata.title}}"
}
```

## 样式系统

### 预定义样式

系统提供多个预定义样式：

| 样式名称 | 用途 | 字号 |
|---------|------|------|
| `Title` | 文档标题 | 24pt |
| `Heading1` | 一级标题 | 16pt |
| `Heading2` | 二级标题 | 14pt |
| `Heading3` | 三级标题 | 12pt |
| `Normal` | 正文 | 10pt |
| `BodyText` | 正文（带缩进） | 10pt |
| `Italic` | 斜体 | 10pt |
| `Bold` | 粗体 | 10pt |

### 自定义样式

```json
{
  "styles": {
    "CustomStyle": {
      "fontName": "SimHei",
      "fontSize": 12,
      "textColor": "#333333",
      "alignment": "left",
      "spaceBefore": 6,
      "spaceAfter": 6
    }
  },
  "elements": [
    {
      "type": "text",
      "content": "自定义样式文本",
      "style": "CustomStyle"
    }
  ]
}
```

### 样式继承

可以基于已有样式创建新样式：

```json
{
  "styles": {
    "HighlightText": {
      "parent": "Normal",
      "textColor": "#FF0000",
      "fontSize": 12
    }
  }
}
```

## 高级功能组件

### 页眉页脚（Page Template）

```json
{
  "pageTemplate": {
    "header": {
      "enabled": true,
      "left": {"type": "text", "content": "{{metadata.title}}"},
      "right": {"type": "text", "content": "{{date}}"}
    },
    "footer": {
      "enabled": true,
      "center": {"type": "pageNumber", "format": "{page}/{total}"}
    }
  }
}
```

### 目录（Table of Contents）

```json
{
  "toc": {
    "enabled": true,
    "autoGenerate": true,
    "title": "目录",
    "maxLevel": 3
  }
}
```

### 封面页（Cover Page）

```json
{
  "coverPage": {
    "enabled": true,
    "background": {
      "type": "gradient",
      "colorStart": "#1e3c72",
      "colorEnd": "#2a5298"
    },
    "elements": [...]
  }
}
```

## 生成模式

### 文件模式

直接生成PDF文件：

```python
generator = PDFReportGenerator(config_path="config.json")
generator.save("output.pdf")
```

### 字节流模式

生成PDF字节流（用于Web服务）：

```python
pdf_bytes = generator.to_bytes()
# 可以直接返回给客户端或保存到数据库
```

### 流式模式

对于大型报告，可以使用流式生成：

```python
with open("output.pdf", "wb") as f:
    generator.generate(output=f)
```

## 坐标系统

### ReportLab坐标系

PDF使用笛卡尔坐标系：

- **原点**：页面左下角 (0, 0)
- **X轴**：从左到右
- **Y轴**：从下到上

### A4页面尺寸

- 宽度：595.27点（约210mm）
- 高度：841.89点（约297mm）

### 常用位置计算

```python
# 页面中心
center_x = 595.27 / 2  # ≈ 297.64
center_y = 841.89 / 2  # ≈ 420.95

# 顶部（距顶部50点）
top_y = 841.89 - 50    # ≈ 791.89

# 底部（距底部50点）
bottom_y = 50
```

## 单位换算

### 常用单位

```python
from reportlab.lib.units import inch, cm, mm

1 inch = 72 点
1 cm = 28.35 点
1 mm = 2.835 点
```

### 换算示例

```python
# 2厘米的间隔
spacer_height = 2 * cm  # = 56.7 点

# 1英寸的边距
margin = 1 * inch  # = 72 点
```

## 错误处理

### 配置验证

系统会自动验证配置文件：

```python
from pdf_generator.config.validator import ConfigValidator

validator = ConfigValidator()
errors = validator.validate(config)
if errors:
    print("配置错误：", errors)
```

### 常见错误

1. **数据源不存在**
   ```
   错误：Data source 'sales' not found
   解决：检查数据源名称拼写
   ```

2. **列名错误**
   ```
   错误：Column 'Sales' not found in data
   解决：检查CSV/数据库列名
   ```

3. **样式未定义**
   ```
   错误：Style 'CustomStyle' not defined
   解决：在styles中定义样式或使用预定义样式
   ```

## 最佳实践

### 1. 配置组织

```
project/
├── configs/
│   ├── base_config.json      # 基础配置
│   ├── sales_report.json     # 销售报告
│   └── financial_report.json # 财务报告
├── data/
│   ├── sales.csv
│   └── products.json
└── output/
    └── reports/
```

### 2. 模块化设计

将大型配置拆分为多个模块：

```python
# 基础配置
base_config = {...}

# 扩展配置
report_config = {
    **base_config,
    "elements": [...]
}
```

### 3. 版本控制

为配置文件添加版本信息：

```json
{
  "version": "1.0.0",
  "metadata": {...},
  ...
}
```

### 4. 文档注释

在JSON中使用 `_comment` 字段添加说明：

```json
{
  "_comment": "这是销售报告的主配置文件",
  "metadata": {
    "_comment": "报告元数据",
    "title": "销售报告"
  }
}
```

## 下一步

了解基本概念后，建议继续学习：

1. **[配置文件总览](./configuration-overview.md)** - 完整的配置结构
2. **[数据源详解](./data-sources.md)** - 深入了解各类数据源
3. **[元素详解](./elements/)** - 学习所有元素类型
4. **[样式系统](./styles.md)** - 掌握样式定制

---

**上一页**：[部署指南](../01-getting-started/deployment.md)  
**下一页**：[配置文件总览](./configuration-overview.md)

