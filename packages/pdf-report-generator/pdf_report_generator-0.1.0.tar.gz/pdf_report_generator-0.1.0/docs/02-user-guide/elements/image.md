# 图片元素

图片元素用于在PDF中插入图片。

## 基本图片

```json
{
  "type": "image",
  "path": "images/logo.png",
  "width": 200
}
```

## 配置选项

### 完整配置

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

### 对齐方式

```json
{
  "alignment": "left"    // 左对齐
  "alignment": "center"  // 居中
  "alignment": "right"   // 右对齐
}
```

## 支持的图片格式

- PNG
- JPEG/JPG
- GIF
- BMP

## 图片尺寸

### 指定宽度（保持比例）

```json
{
  "type": "image",
  "path": "logo.png",
  "width": 200
}
```

### 指定宽度和高度

```json
{
  "type": "image",
  "path": "banner.png",
  "width": 500,
  "height": 100,
  "preserveAspectRatio": false
}
```

---

**上一页**：[图表元素](./chart.md)  
**下一页**：[其他元素](./others.md)

