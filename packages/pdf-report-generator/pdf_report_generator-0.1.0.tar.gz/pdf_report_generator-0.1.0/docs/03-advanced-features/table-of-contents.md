# 自动目录

自动目录功能可以根据文档中的标题自动生成可点击的目录。

## 启用自动目录

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

## 目录配置

### 完整配置

```json
{
  "toc": {
    "enabled": true,
    "autoGenerate": true,
    "title": "目  录",
    "maxLevel": 2,
    "showPageNumbers": true
  }
}
```

## 手动目录

```json
{
  "toc": {
    "enabled": true,
    "autoGenerate": false,
    "entries": [
      {"level": 1, "title": "第一章", "pageNum": 3},
      {"level": 2, "title": "1.1 概述", "pageNum": 3},
      {"level": 1, "title": "第二章", "pageNum": 5}
    ]
  }
}
```

## 标题级别

使用heading元素时会自动添加到目录：

```json
{
  "elements": [
    {"type": "heading", "text": "第一章", "level": 1},
    {"type": "heading", "text": "1.1 节", "level": 2},
    {"type": "heading", "text": "1.1.1 小节", "level": 3}
  ]
}
```

---

**上一页**：[页眉页脚](./headers-footers.md)  
**下一页**：[封面设计](./cover-pages.md)

