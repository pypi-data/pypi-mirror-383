# 配置文件总览

本文档提供PDF报告生成器配置文件的完整结构说明和示例。

## 完整配置结构

```json
{
  "version": "1.0",
  "metadata": {...},
  "styles": {...},
  "coverPage": {...},
  "toc": {...},
  "pageTemplate": {...},
  "dataSources": [...],
  "elements": [...]
}
```

## 1. 版本信息（可选）

```json
{
  "version": "1.0.0",
  "_comment": "配置文件版本号"
}
```

## 2. 元数据配置

### 基本元数据

```json
{
  "metadata": {
    "title": "报告标题",
    "author": "作者姓名",
    "subject": "报告主题",
    "keywords": "关键词1, 关键词2",
    "company": "公司名称",
    
    "pageSize": "A4",
    "orientation": "portrait",
    
    "leftMargin": 72,
    "rightMargin": 72,
    "topMargin": 72,
    "bottomMargin": 72
  }
}
```

### 页面尺寸选项

| 值 | 尺寸 | 说明 |
|---|------|------|
| `A4` | 210×297mm | 默认值 |
| `A3` | 297×420mm | 大页面 |
| `A5` | 148×210mm | 小页面 |
| `LETTER` | 8.5×11in | 美国信纸 |
| `LEGAL` | 8.5×14in | 美国法律文书 |

### 页面方向

- `portrait`：纵向（默认）
- `landscape`：横向

### 边距设置

边距单位为点（1英寸 = 72点）：

```json
{
  "metadata": {
    "leftMargin": 54,    // 0.75英寸
    "rightMargin": 54,
    "topMargin": 72,     // 1英寸
    "bottomMargin": 72
  }
}
```

## 3. 样式配置

### 段落样式

```json
{
  "styles": {
    "CustomHeading": {
      "fontName": "SimHei",
      "fontSize": 18,
      "textColor": "#1a1a1a",
      "alignment": "center",
      "spaceBefore": 12,
      "spaceAfter": 12,
      "leading": 22,
      "leftIndent": 0,
      "rightIndent": 0,
      "firstLineIndent": 0
    }
  }
}
```

### 样式属性说明

| 属性 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `fontName` | string | 字体名称 | "SimHei" |
| `fontSize` | number | 字号（点） | 10 |
| `textColor` | string | 文字颜色（十六进制） | "#000000" |
| `alignment` | string | 对齐方式 | "left" |
| `spaceBefore` | number | 段前间距（点） | 0 |
| `spaceAfter` | number | 段后间距（点） | 0 |
| `leading` | number | 行距（点） | fontSize*1.2 |
| `leftIndent` | number | 左缩进（点） | 0 |
| `rightIndent` | number | 右缩进（点） | 0 |
| `firstLineIndent` | number | 首行缩进（点） | 0 |

### 对齐方式

- `left`：左对齐
- `center`：居中
- `right`：右对齐
- `justify`：两端对齐

### 表格样式

```json
{
  "styles": {
    "CustomTable": {
      "gridColor": "#CCCCCC",
      "gridWidth": 0.5,
      "headerBackgroundColor": "#4472C4",
      "headerTextColor": "#FFFFFF",
      "headerFontSize": 11,
      "alternateRowColor": "#F2F2F2",
      "fontSize": 9,
      "alignment": "center",
      "cellPadding": 6
    }
  }
}
```

## 4. 封面页配置

### 基本封面

```json
{
  "coverPage": {
    "enabled": true,
    "background": {
      "type": "color",
      "color": "#FFFFFF"
    },
    "elements": [
      {
        "type": "text",
        "content": "{{metadata.title}}",
        "style": "Title",
        "position": {"x": "center", "y": 600}
      }
    ]
  }
}
```

### 背景类型

#### 纯色背景

```json
{
  "background": {
    "type": "color",
    "color": "#2C3E50",
    "opacity": 1.0
  }
}
```

#### 渐变背景

```json
{
  "background": {
    "type": "gradient",
    "colorStart": "#1e3c72",
    "colorEnd": "#2a5298"
  }
}
```

#### 图片背景

```json
{
  "background": {
    "type": "image",
    "path": "cover_bg.jpg",
    "opacity": 0.5
  }
}
```

### 封面元素

```json
{
  "coverPage": {
    "elements": [
      {
        "type": "text",
        "content": "报告标题",
        "style": "Title",
        "position": {"x": "center", "y": 600}
      },
      {
        "type": "image",
        "path": "logo.png",
        "width": 200,
        "position": {"x": "center", "y": 400}
      }
    ]
  }
}
```

### 位置坐标

- **x坐标**：`"left"`, `"center"`, `"right"` 或数值（点）
- **y坐标**：`"top"`, `"center"`, `"bottom"` 或数值（点）

## 5. 目录配置

### 自动目录

```json
{
  "toc": {
    "enabled": true,
    "autoGenerate": true,
    "title": "目  录",
    "maxLevel": 3
  }
}
```

### 手动目录

```json
{
  "toc": {
    "enabled": true,
    "autoGenerate": false,
    "title": "目录",
    "entries": [
      {
        "level": 1,
        "title": "第一章 概述",
        "pageNum": 3
      },
      {
        "level": 2,
        "title": "1.1 背景",
        "pageNum": 3
      }
    ]
  }
}
```

### 目录选项

| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `enabled` | boolean | 是否启用 | false |
| `autoGenerate` | boolean | 自动生成 | true |
| `title` | string | 目录标题 | "目录" |
| `maxLevel` | number | 最大层级 | 3 |

## 6. 页眉页脚配置

### 完整示例

```json
{
  "pageTemplate": {
    "header": {
      "enabled": true,
      "height": 0.8,
      "showLine": true,
      "left": {
        "type": "text",
        "content": "{{metadata.title}}",
        "fontName": "SimHei",
        "fontSize": 9,
        "color": "#666666"
      },
      "center": {
        "type": "image",
        "path": "logo.png",
        "width": 60,
        "height": 30
      },
      "right": {
        "type": "text",
        "content": "{{date}}",
        "fontName": "SimHei",
        "fontSize": 9
      }
    },
    "footer": {
      "enabled": true,
      "height": 0.6,
      "showLine": true,
      "left": {
        "type": "text",
        "content": "{{metadata.company}}"
      },
      "center": {
        "type": "pageNumber",
        "format": "第 {page} 页 共 {total} 页"
      },
      "right": {
        "type": "text",
        "content": "{{metadata.author}}"
      }
    }
  }
}
```

### 页码格式

```json
{
  "type": "pageNumber",
  "format": "{page}"           // 1, 2, 3...
  // "format": "{roman}"        // i, ii, iii...
  // "format": "{chinese}"      // 一, 二, 三...
  // "format": "- {page} -"     // - 1 -, - 2 -...
  // "format": "{page}/{total}" // 1/10, 2/10...
}
```

## 7. 数据源配置

### CSV数据源

```json
{
  "dataSources": [
    {
      "name": "sales_data",
      "type": "csv",
      "path": "data/sales.csv",
      "encoding": "utf-8",
      "delimiter": ",",
      "skiprows": 0
    }
  ]
}
```

### JSON数据源

```json
{
  "dataSources": [
    {
      "name": "products",
      "type": "json",
      "path": "data/products.json",
      "jsonPath": "$.data.products",
      "encoding": "utf-8"
    }
  ]
}
```

### Excel数据源

```json
{
  "dataSources": [
    {
      "name": "budget",
      "type": "excel",
      "path": "data/budget.xlsx",
      "sheet": "2024年预算",
      "skiprows": 1,
      "usecols": "A:F"
    }
  ]
}
```

### API数据源

```json
{
  "dataSources": [
    {
      "name": "api_sales",
      "type": "api",
      "url": "https://api.example.com/sales",
      "method": "GET",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN",
        "Content-Type": "application/json"
      },
      "params": {
        "year": "2024",
        "quarter": "Q1"
      },
      "jsonPath": "$.data"
    }
  ]
}
```

### 数据库数据源

```json
{
  "dataSources": [
    {
      "name": "db_orders",
      "type": "database",
      "connection": "postgresql://user:pass@localhost/mydb",
      "query": "SELECT * FROM orders WHERE year = 2024",
      "params": {}
    }
  ]
}
```

### 内联数据源

```json
{
  "dataSources": [
    {
      "name": "summary",
      "type": "inline",
      "data": [
        {"指标": "总销售额", "值": "¥1,000,000"},
        {"指标": "增长率", "值": "15%"}
      ]
    }
  ]
}
```

## 8. 元素配置

### 文本元素

```json
{
  "type": "text",
  "content": "这是一段文本内容",
  "style": "Normal",
  "alignment": "left"
}
```

### 标题元素

```json
{
  "type": "heading",
  "text": "第一章 报告概述",
  "level": 1,
  "style": "Heading1"
}
```

### 表格元素

```json
{
  "type": "table",
  "dataSource": "sales_data",
  "columns": ["产品", "销量", "金额"],
  "style": {
    "gridColor": "#CCCCCC",
    "headerBackgroundColor": "#4472C4",
    "alternateRowColor": "#F2F2F2"
  }
}
```

### 图表元素

```json
{
  "type": "chart",
  "chartType": "bar",
  "dataSource": "sales_data",
  "xColumn": "月份",
  "yColumn": "销售额",
  "title": "月度销售趋势",
  "width": 450,
  "height": 300,
  "colors": ["#4472C4"],
  "showLegend": true
}
```

### 图片元素

```json
{
  "type": "image",
  "path": "images/chart.png",
  "width": 400,
  "height": 300,
  "alignment": "center",
  "preserveAspectRatio": true
}
```

### 分页符

```json
{
  "type": "pageBreak"
}
```

### 间隔

```json
{
  "type": "spacer",
  "height": 20
}
```

### 列表

```json
{
  "type": "list",
  "items": [
    "第一项",
    "第二项",
    "第三项"
  ],
  "bulletType": "bullet",  // bullet, numbered, alpha
  "style": "Normal"
}
```

## 完整配置示例

```json
{
  "metadata": {
    "title": "2024年销售分析报告",
    "author": "数据分析部",
    "company": "ABC科技公司",
    "pageSize": "A4",
    "orientation": "portrait"
  },
  
  "styles": {
    "CustomHeading": {
      "fontName": "SimHei",
      "fontSize": 16,
      "textColor": "#2C3E50",
      "spaceBefore": 12,
      "spaceAfter": 12
    }
  },
  
  "coverPage": {
    "enabled": true,
    "background": {
      "type": "gradient",
      "colorStart": "#1e3c72",
      "colorEnd": "#2a5298"
    },
    "elements": [
      {
        "type": "text",
        "content": "{{metadata.title}}",
        "style": "Title",
        "position": {"x": "center", "y": 600}
      }
    ]
  },
  
  "toc": {
    "enabled": true,
    "autoGenerate": true,
    "title": "目录",
    "maxLevel": 2
  },
  
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
  },
  
  "dataSources": [
    {
      "name": "sales",
      "type": "csv",
      "path": "data/sales.csv"
    }
  ],
  
  "elements": [
    {
      "type": "heading",
      "text": "第一章 销售概况",
      "level": 1
    },
    {
      "type": "text",
      "content": "本章分析2024年的销售情况。"
    },
    {
      "type": "table",
      "dataSource": "sales"
    },
    {
      "type": "chart",
      "chartType": "line",
      "dataSource": "sales",
      "xColumn": "月份",
      "yColumn": "销售额",
      "title": "销售趋势"
    }
  ]
}
```

## 配置验证

### 使用Schema验证

项目提供了JSON Schema文件用于验证配置：

```python
import json
import jsonschema

# 加载schema
with open('templates/template_schema.json') as f:
    schema = json.load(f)

# 加载配置
with open('my_config.json') as f:
    config = json.load(f)

# 验证
try:
    jsonschema.validate(config, schema)
    print("✅ 配置验证通过")
except jsonschema.ValidationError as e:
    print(f"❌ 配置错误: {e.message}")
```

### 使用Python API验证

```python
from pdf_generator.config.validator import ConfigValidator

validator = ConfigValidator()
errors = validator.validate(config)

if errors:
    for error in errors:
        print(f"错误: {error}")
else:
    print("✅ 配置正确")
```

## 配置最佳实践

### 1. 使用变量减少重复

```json
{
  "metadata": {
    "company": "ABC公司",
    "year": "2024"
  },
  "elements": [
    {
      "type": "text",
      "content": "{{metadata.company}}{{metadata.year}}年度报告"
    }
  ]
}
```

### 2. 分离样式定义

```json
{
  "styles": {
    "SectionHeading": {...},
    "DataTable": {...}
  },
  "elements": [
    {
      "type": "heading",
      "style": "SectionHeading",
      ...
    }
  ]
}
```

### 3. 模块化数据源

```json
{
  "dataSources": [
    {"name": "sales", "type": "csv", "path": "sales.csv"},
    {"name": "costs", "type": "csv", "path": "costs.csv"},
    {"name": "profit", "type": "csv", "path": "profit.csv"}
  ]
}
```

### 4. 使用注释

```json
{
  "_comment": "销售报告主配置",
  "metadata": {
    "_comment": "报告元数据",
    "title": "销售报告"
  }
}
```

## 下一步

- **[数据源详解](./data-sources.md)** - 深入了解数据源
- **[样式系统](./styles.md)** - 掌握样式定制
- **[元素详解](./elements/)** - 学习各类元素
- **[模板变量](./templates.md)** - 使用模板语法

---

**上一页**：[基本概念](./basic-concepts.md)  
**下一页**：[数据源详解](./data-sources.md)

