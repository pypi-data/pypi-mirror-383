# 图片处理

图片高级处理技巧。

## 图片格式支持

- PNG
- JPEG/JPG
- GIF
- BMP

## 尺寸控制

### 保持比例

```json
{
  "type": "image",
  "path": "image.png",
  "width": 400,
  "preserveAspectRatio": true
}
```

### 固定尺寸

```json
{
  "type": "image",
  "path": "image.png",
  "width": 400,
  "height": 300,
  "preserveAspectRatio": false
}
```

## 对齐方式

```json
{
  "alignment": "left"    // 左对齐
  "alignment": "center"  // 居中
  "alignment": "right"   // 右对齐
}
```

---

**上一页**：[中文字体](./chinese-fonts.md)  
**下一页**：[页码格式](./page-numbers.md)

