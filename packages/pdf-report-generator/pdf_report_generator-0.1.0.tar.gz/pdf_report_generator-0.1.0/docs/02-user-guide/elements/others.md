# 其他元素

本文档介绍其他辅助性PDF元素。

## 分页符

强制开始新页面：

```json
{
  "type": "pageBreak"
}
```

## 间隔

添加垂直空白间距：

```json
{
  "type": "spacer",
  "height": 20  // 高度（点）
}
```

### 常用间距

```json
{"type": "spacer", "height": 10}   // 小间距
{"type": "spacer", "height": 20}   // 中间距
{"type": "spacer", "height": 40}   // 大间距
```

## 水平线

```json
{
  "type": "line",
  "width": "100%",
  "color": "#CCCCCC",
  "thickness": 1
}
```

## 组合使用

### 章节分隔

```json
{
  "elements": [
    {"type": "heading", "text": "第一章", "level": 1},
    {"type": "text", "content": "章节内容..."},
    {"type": "spacer", "height": 30},
    {"type": "line"},
    {"type": "pageBreak"},
    {"type": "heading", "text": "第二章", "level": 1}
  ]
}
```

---

**上一页**：[图片元素](./image.md)  
**下一页**：[高级功能](../../03-advanced-features/)

