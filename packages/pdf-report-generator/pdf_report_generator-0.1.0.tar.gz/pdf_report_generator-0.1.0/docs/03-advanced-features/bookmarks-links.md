# 书签和链接

PDF书签和超链接功能。

## 自动书签

启用自动目录时，标题会自动添加为书签：

```json
{
  "toc": {
    "enabled": true,
    "autoGenerate": true
  },
  "elements": [
    {"type": "heading", "text": "第一章", "level": 1}
  ]
}
```

## PDF大纲

标题自动添加到PDF大纲，可在PDF阅读器中导航。

## 内部链接

目录中的条目自动包含到对应章节的超链接。

## 最佳实践

- 使用清晰的标题层次结构
- 启用自动目录生成书签
- 保持标题简洁明了

---

**上一页**：[页码格式](./page-numbers.md)  
**下一页**：[API参考](../04-api-reference/)

