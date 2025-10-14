# 封面设计

封面页功能允许创建精美的报告封面。

## 基本封面

```json
{
  "coverPage": {
    "enabled": true,
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

## 背景设置

### 纯色背景

```json
{
  "coverPage": {
    "background": {
      "type": "color",
      "color": "#2C3E50"
    }
  }
}
```

### 渐变背景

```json
{
  "coverPage": {
    "background": {
      "type": "gradient",
      "colorStart": "#1e3c72",
      "colorEnd": "#2a5298"
    }
  }
}
```

### 图片背景

```json
{
  "coverPage": {
    "background": {
      "type": "image",
      "path": "cover.jpg",
      "opacity": 0.5
    }
  }
}
```

## 封面元素

### 文本元素

```json
{
  "type": "text",
  "content": "报告标题",
  "style": "Title",
  "position": {"x": "center", "y": 600}
}
```

### 图片元素

```json
{
  "type": "image",
  "path": "logo.png",
  "width": 200,
  "position": {"x": "center", "y": 400}
}
```

## 位置坐标

- x: "left", "center", "right" 或数值
- y: "top", "center", "bottom" 或数值

---

**上一页**：[自动目录](./table-of-contents.md)  
**下一页**：[表格合并](./table-merging.md)

