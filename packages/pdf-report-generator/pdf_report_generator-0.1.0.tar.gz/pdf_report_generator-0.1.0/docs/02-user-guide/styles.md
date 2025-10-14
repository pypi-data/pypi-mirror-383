# 样式系统

PDF报告生成器提供了灵活的样式系统，支持预定义样式和自定义样式。

## 预定义样式

系统提供了常用的预定义样式，可直接使用。

### 文本样式

| 样式名 | 用途 | 字号 | 字体 | 特点 |
|--------|------|------|------|------|
| `Title` | 文档标题 | 24pt | SimHei | 加粗、居中 |
| `Heading1` | 一级标题 | 16pt | SimHei | 加粗 |
| `Heading2` | 二级标题 | 14pt | SimHei | 加粗 |
| `Heading3` | 三级标题 | 12pt | SimHei | 加粗 |
| `Normal` | 正文 | 10pt | SimSun | 常规 |
| `BodyText` | 正文（缩进） | 10pt | SimSun | 首行缩进 |
| `Italic` | 斜体 | 10pt | SimSun | 斜体 |
| `Bold` | 粗体 | 10pt | SimHei | 加粗 |
| `Code` | 代码 | 9pt | Courier | 等宽字体 |

### 使用预定义样式

```json
{
  "elements": [
    {
      "type": "text",
      "content": "这是标题",
      "style": "Heading1"
    },
    {
      "type": "text",
      "content": "这是正文内容",
      "style": "Normal"
    }
  ]
}
```

## 自定义样式

### 定义自定义样式

在配置文件的 `styles` 部分定义：

```json
{
  "styles": {
    "MyCustomStyle": {
      "fontName": "SimHei",
      "fontSize": 12,
      "textColor": "#2C3E50",
      "alignment": "left",
      "spaceBefore": 10,
      "spaceAfter": 10,
      "leading": 18,
      "leftIndent": 0,
      "rightIndent": 0,
      "firstLineIndent": 0
    }
  }
}
```

### 样式属性完整列表

#### 字体属性

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `fontName` | string | 字体名称 | "SimHei", "SimSun" |
| `fontSize` | number | 字号（点） | 12 |
| `textColor` | string | 文字颜色 | "#FF0000", "red" |

#### 对齐和间距

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `alignment` | string | 对齐方式 | "left", "center", "right", "justify" |
| `spaceBefore` | number | 段前间距（点） | 10 |
| `spaceAfter` | number | 段后间距（点） | 10 |
| `leading` | number | 行距（点） | 18 |

#### 缩进属性

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `leftIndent` | number | 左缩进（点） | 20 |
| `rightIndent` | number | 右缩进（点） | 0 |
| `firstLineIndent` | number | 首行缩进（点） | 28 |

### 使用自定义样式

```json
{
  "styles": {
    "HighlightText": {
      "fontName": "SimHei",
      "fontSize": 14,
      "textColor": "#FF6B6B",
      "alignment": "center"
    }
  },
  "elements": [
    {
      "type": "text",
      "content": "重要提示！",
      "style": "HighlightText"
    }
  ]
}
```

## 样式继承

### 从预定义样式继承

```json
{
  "styles": {
    "MyHeading": {
      "parent": "Heading1",
      "textColor": "#4472C4",
      "spaceBefore": 20
    }
  }
}
```

这样 `MyHeading` 会继承 `Heading1` 的所有属性，并覆盖指定的属性。

### 多级继承

```json
{
  "styles": {
    "BaseHeading": {
      "fontName": "SimHei",
      "fontSize": 14,
      "textColor": "#333333"
    },
    "BlueHeading": {
      "parent": "BaseHeading",
      "textColor": "#4472C4"
    },
    "LargeBlueHeading": {
      "parent": "BlueHeading",
      "fontSize": 18
    }
  }
}
```

## 表格样式

### 基本表格样式

```json
{
  "type": "table",
  "dataSource": "sales",
  "style": {
    "gridColor": "#CCCCCC",
    "gridWidth": 0.5,
    "alignment": "center"
  }
}
```

### 完整表格样式

```json
{
  "type": "table",
  "dataSource": "data",
  "style": {
    "gridColor": "#DDDDDD",
    "gridWidth": 1,
    "headerBackgroundColor": "#4472C4",
    "headerTextColor": "#FFFFFF",
    "headerFontSize": 11,
    "headerFontName": "SimHei",
    "alternateRowColor": "#F2F2F2",
    "fontSize": 9,
    "fontName": "SimSun",
    "textColor": "#333333",
    "alignment": "center",
    "cellPadding": 6
  }
}
```

### 表格样式属性

| 属性 | 说明 | 默认值 |
|------|------|--------|
| `gridColor` | 网格线颜色 | "#CCCCCC" |
| `gridWidth` | 网格线宽度（点） | 0.5 |
| `headerBackgroundColor` | 表头背景色 | "#FFFFFF" |
| `headerTextColor` | 表头文字颜色 | "#000000" |
| `headerFontSize` | 表头字号 | 11 |
| `headerFontName` | 表头字体 | "SimHei" |
| `alternateRowColor` | 交替行颜色 | - |
| `fontSize` | 单元格字号 | 9 |
| `fontName` | 单元格字体 | "SimSun" |
| `textColor` | 单元格文字颜色 | "#000000" |
| `alignment` | 对齐方式 | "left" |
| `cellPadding` | 单元格内边距 | 3 |

### 表格样式复用

定义可复用的表格样式：

```json
{
  "styles": {
    "DataTable": {
      "gridColor": "#CCCCCC",
      "headerBackgroundColor": "#4472C4",
      "alternateRowColor": "#F0F0F0"
    },
    "FinancialTable": {
      "gridColor": "#70AD47",
      "headerBackgroundColor": "#70AD47",
      "headerTextColor": "#FFFFFF",
      "alternateRowColor": "#E2EFDA"
    }
  },
  "elements": [
    {
      "type": "table",
      "dataSource": "sales",
      "style": "DataTable"
    },
    {
      "type": "table",
      "dataSource": "budget",
      "style": "FinancialTable"
    }
  ]
}
```

## 颜色系统

### 颜色格式

支持多种颜色格式：

```json
{
  "textColor": "#FF0000"      // 十六进制
  "textColor": "#F00"         // 短十六进制
  "textColor": "red"          // 颜色名称（部分支持）
}
```

### 常用颜色值

| 颜色 | 十六进制 | 用途 |
|------|---------|------|
| 黑色 | #000000 | 正文 |
| 深灰 | #333333 | 副标题 |
| 灰色 | #666666 | 辅助文字 |
| 浅灰 | #CCCCCC | 边框 |
| 蓝色 | #4472C4 | 主题色 |
| 绿色 | #70AD47 | 成功/财务 |
| 红色 | #FF0000 | 警告/重要 |
| 橙色 | #ED7D31 | 提示 |

### 配色方案示例

#### 商务风格

```json
{
  "styles": {
    "BusinessHeading": {
      "textColor": "#2C3E50",
      "fontName": "SimHei"
    },
    "BusinessTable": {
      "headerBackgroundColor": "#34495E",
      "alternateRowColor": "#ECF0F1"
    }
  }
}
```

#### 科技风格

```json
{
  "styles": {
    "TechHeading": {
      "textColor": "#3498DB",
      "fontName": "SimHei"
    },
    "TechTable": {
      "headerBackgroundColor": "#2980B9",
      "alternateRowColor": "#EBF5FB"
    }
  }
}
```

#### 财务风格

```json
{
  "styles": {
    "FinanceHeading": {
      "textColor": "#27AE60",
      "fontName": "SimHei"
    },
    "FinanceTable": {
      "headerBackgroundColor": "#229954",
      "alternateRowColor": "#E8F8F5"
    }
  }
}
```

## 字体管理

### 可用字体

系统默认包含：

- **SimHei** - 黑体（中文）
- **SimSun** - 宋体（中文）
- **GB2312** - GB2312字体
- **Helvetica** - 西文字体
- **Times-Roman** - 西文衬线字体
- **Courier** - 等宽字体

### 添加自定义字体

```python
from pdf_generator.core.styles import StyleManager

style_manager = StyleManager()

# 注册自定义字体
style_manager.register_font(
    "CustomFont",
    "path/to/font.ttf"
)

# 在样式中使用
config = {
  "styles": {
    "MyStyle": {
      "fontName": "CustomFont",
      "fontSize": 12
    }
  }
}
```

### 字体回退

当指定字体不可用时，系统会自动回退：

```
指定字体 → SimHei → Helvetica
```

## 单位和度量

### ReportLab单位

```python
from reportlab.lib.units import inch, cm, mm

1 inch = 72 点
1 cm = 28.35 点
1 mm = 2.835 点
```

### 常用尺寸

```json
{
  "fontSize": 12,        // 字号（点）
  "spaceBefore": 14,     // 0.5厘米
  "leading": 18,         // 1.5倍行距
  "leftIndent": 28       // 1厘米
}
```

### 尺寸计算

```python
# Python中计算
from reportlab.lib.units import cm

config = {
  "spaceBefore": 1 * cm,    # 1厘米 = 28.35点
  "leftIndent": 0.5 * cm    # 0.5厘米 = 14.175点
}
```

## 样式最佳实践

### 1. 建立样式系统

```json
{
  "styles": {
    "DocTitle": {...},
    "ChapterHeading": {...},
    "SectionHeading": {...},
    "NormalText": {...},
    "ImportantText": {...},
    "DataTable": {...}
  }
}
```

### 2. 保持一致性

```json
{
  "styles": {
    "BaseHeading": {
      "fontName": "SimHei",
      "textColor": "#2C3E50"
    },
    "H1": {
      "parent": "BaseHeading",
      "fontSize": 18
    },
    "H2": {
      "parent": "BaseHeading",
      "fontSize": 14
    }
  }
}
```

### 3. 使用语义化命名

```json
{
  "styles": {
    "SuccessText": {"textColor": "#27AE60"},
    "WarningText": {"textColor": "#E67E22"},
    "ErrorText": {"textColor": "#E74C3C"}
  }
}
```

### 4. 主题化设计

```json
{
  "styles": {
    "_theme": {
      "primaryColor": "#4472C4",
      "secondaryColor": "#ED7D31",
      "textColor": "#333333"
    },
    "PrimaryHeading": {
      "textColor": "{{_theme.primaryColor}}"
    }
  }
}
```

## 响应式样式

### 根据页面大小调整

```python
page_size = "A4"  # 或 "A3", "LETTER"

if page_size == "A3":
    font_size = 14
elif page_size == "A4":
    font_size = 12
else:
    font_size = 10

config = {
  "styles": {
    "Normal": {"fontSize": font_size}
  }
}
```

### 根据内容调整

```python
# 长报告使用较小字号
if len(content) > 10000:
    body_font = 9
else:
    body_font = 10
```

## 调试样式

### 查看应用的样式

```python
from pdf_generator import PDFReportGenerator

generator = PDFReportGenerator(config_path="config.json")

# 获取样式
style = generator.style_manager.get_style("Heading1")
print(f"字体: {style.fontName}")
print(f"字号: {style.fontSize}")
print(f"颜色: {style.textColor}")
```

### 样式对比

```python
# 比较两个样式
style1 = style_manager.get_style("Normal")
style2 = style_manager.get_style("BodyText")

print(f"Normal firstLineIndent: {style1.firstLineIndent}")
print(f"BodyText firstLineIndent: {style2.firstLineIndent}")
```

## 常见问题

### Q: 中文字体不显示？

确保使用支持中文的字体：

```json
{
  "fontName": "SimHei"  // 或 "SimSun", "GB2312"
}
```

### Q: 颜色不生效？

检查颜色格式：

```json
{
  "textColor": "#FF0000"  // ✅ 正确
  "textColor": "FF0000"   // ❌ 缺少#
}
```

### Q: 表格样式被覆盖？

元素级样式优先于全局样式：

```json
{
  "type": "table",
  "style": {  // 元素级样式，优先级最高
    "fontSize": 10
  }
}
```

## 下一步

- **[模板变量](./templates.md)** - 在样式中使用变量
- **[文本元素](./elements/text.md)** - 应用文本样式
- **[表格元素](./elements/table.md)** - 应用表格样式

---

**上一页**：[数据源详解](./data-sources.md)  
**下一页**：[模板变量](./templates.md)

