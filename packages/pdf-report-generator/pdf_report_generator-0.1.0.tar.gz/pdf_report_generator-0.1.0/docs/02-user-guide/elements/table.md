# 表格元素

表格元素用于展示结构化数据。

## 基本表格

```json
{
  "type": "table",
  "dataSource": "sales_data"
}
```

## 配置选项

### 指定列

```json
{
  "type": "table",
  "dataSource": "sales_data",
  "columns": ["产品", "销量", "金额"]
}
```

### 表格样式

```json
{
  "type": "table",
  "dataSource": "sales_data",
  "style": {
    "gridColor": "#CCCCCC",
    "headerBackgroundColor": "#4472C4",
    "headerTextColor": "#FFFFFF",
    "alternateRowColor": "#F2F2F2",
    "fontSize": 9,
    "alignment": "center"
  }
}
```

## 单元格合并

```json
{
  "type": "table",
  "dataSource": "data",
  "mergeRules": [
    {
      "startRow": 0,
      "startCol": 0,
      "endRow": 0,
      "endCol": 1
    }
  ]
}
```

## 列格式化

```json
{
  "type": "table",
  "dataSource": "sales",
  "columnFormats": {
    "金额": "¥{:,.2f}",
    "增长率": "{:.1%}"
  }
}
```

---

**上一页**：[文本元素](./text.md)  
**下一页**：[图表元素](./chart.md)

