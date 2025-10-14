# 文本元素

文本元素是PDF报告中最基本的内容单元，用于显示文字信息。

## 基本文本

### 简单文本

```json
{
  "type": "text",
  "content": "这是一段简单的文本"
}
```

### 使用样式

```json
{
  "type": "text",
  "content": "这是一段使用自定义样式的文本",
  "style": "Normal"
}
```

## 文本配置选项

### 完整配置

```json
{
  "type": "text",
  "content": "文本内容",
  "style": "Normal",
  "alignment": "left",
  "fontSize": 12,
  "textColor": "#000000",
  "fontName": "SimHei"
}
```

### 对齐方式

```json
{
  "type": "text",
  "content": "左对齐",
  "alignment": "left"
}
{
  "type": "text",
  "content": "居中",
  "alignment": "center"
}
{
  "type": "text",
  "content": "右对齐",
  "alignment": "right"
}
{
  "type": "text",
  "content": "两端对齐",
  "alignment": "justify"
}
```

## 标题元素

### 各级标题

```json
{
  "type": "heading",
  "text": "一级标题",
  "level": 1
}
{
  "type": "heading",
  "text": "二级标题",
  "level": 2
}
{
  "type": "heading",
  "text": "三级标题",
  "level": 3
}
```

### 自定义标题样式

```json
{
  "type": "heading",
  "text": "自定义样式标题",
  "level": 1,
  "style": "CustomHeading"
}
```

## 格式化文本

### HTML标签支持

```json
{
  "type": "text",
  "content": "这是<b>粗体</b>和<i>斜体</i>文本",
  "style": "Normal"
}
```

支持的HTML标签：
- `<b>` - 粗体
- `<i>` - 斜体
- `<u>` - 下划线
- `<br/>` - 换行
- `<font color='#FF0000'>` - 颜色

### 换行处理

```json
{
  "type": "text",
  "content": "第一行<br/>第二行<br/>第三行"
}
```

### 多段落文本

```json
{
  "type": "text",
  "content": "第一段内容\n\n第二段内容\n\n第三段内容"
}
```

## 使用模板变量

### 动态内容

```json
{
  "type": "text",
  "content": "报告日期：{{date}}"
}
{
  "type": "text",
  "content": "作者：{{metadata.author}}"
}
```

### 条件文本

```json
{
  "type": "text",
  "content": "{% if is_urgent %}【紧急】{% endif %}{{title}}"
}
```

## 列表元素

### 无序列表

```json
{
  "type": "list",
  "items": [
    "第一项",
    "第二项",
    "第三项"
  ],
  "bulletType": "bullet"
}
```

### 有序列表

```json
{
  "type": "list",
  "items": [
    "步骤一",
    "步骤二",
    "步骤三"
  ],
  "bulletType": "numbered"
}
```

### 字母列表

```json
{
  "type": "list",
  "items": [
    "选项A",
    "选项B",
    "选项C"
  ],
  "bulletType": "alpha"
}
```

## 实用示例

### 报告摘要

```json
{
  "type": "text",
  "content": "<b>执行摘要</b><br/><br/>本报告分析了2024年第一季度的销售情况，主要发现包括：<br/>• 总销售额达到¥155万元<br/>• 同比增长15%<br/>• 新客户增加440人",
  "style": "BodyText"
}
```

### 强调文本

```json
{
  "type": "text",
  "content": "<font color='#FF0000'><b>重要提示：</b></font>请在3月31日前提交报告",
  "style": "Normal"
}
```

---

**上一页**：[模板变量](../templates.md)  
**下一页**：[表格元素](./table.md)

