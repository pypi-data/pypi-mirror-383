# 图表元素

图表元素用于数据可视化，基于Matplotlib生成。

## 支持的图表类型

- **bar** - 柱状图
- **line** - 折线图
- **pie** - 饼图
- **scatter** - 散点图
- **area** - 面积图

## 柱状图

```json
{
  "type": "chart",
  "chartType": "bar",
  "dataSource": "sales",
  "xColumn": "月份",
  "yColumn": "销售额",
  "title": "月度销售额",
  "width": 450,
  "height": 300
}
```

## 折线图

```json
{
  "type": "chart",
  "chartType": "line",
  "dataSource": "trends",
  "xColumn": "日期",
  "yColumns": ["销售额", "成本", "利润"],
  "title": "趋势分析",
  "showLegend": true,
  "colors": ["#4472C4", "#ED7D31", "#70AD47"]
}
```

## 饼图

```json
{
  "type": "chart",
  "chartType": "pie",
  "dataSource": "market_share",
  "labelColumn": "产品",
  "valueColumn": "份额",
  "title": "市场份额",
  "showLegend": true
}
```

## 图表配置

### 完整选项

```json
{
  "type": "chart",
  "chartType": "bar",
  "dataSource": "data",
  "xColumn": "category",
  "yColumn": "value",
  "title": "图表标题",
  "xlabel": "X轴标签",
  "ylabel": "Y轴标签",
  "width": 500,
  "height": 350,
  "colors": ["#4472C4"],
  "showGrid": true,
  "showLegend": true
}
```

---

**上一页**：[表格元素](./table.md)  
**下一页**：[图片元素](./image.md)

