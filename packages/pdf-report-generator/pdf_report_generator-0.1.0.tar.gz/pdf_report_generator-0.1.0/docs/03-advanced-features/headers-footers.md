# 页眉页脚

页眉页脚功能允许在每页顶部和底部添加内容。

## 基本配置

```json
{
  "pageTemplate": {
    "header": {
      "enabled": true,
      "center": {
        "type": "text",
        "content": "{{metadata.title}}"
      }
    },
    "footer": {
      "enabled": true,
      "center": {
        "type": "pageNumber",
        "format": "{page}/{total}"
      }
    }
  }
}
```

## 三栏布局

```json
{
  "pageTemplate": {
    "header": {
      "enabled": true,
      "left": {"type": "text", "content": "左侧内容"},
      "center": {"type": "text", "content": "中间内容"},
      "right": {"type": "text", "content": "右侧内容"}
    }
  }
}
```

## 页码格式

```json
{
  "type": "pageNumber",
  "format": "{page}"           // 1, 2, 3
  "format": "{roman}"          // i, ii, iii
  "format": "{chinese}"        // 一, 二, 三
  "format": "第 {page} 页"     // 第 1 页
  "format": "{page}/{total}"   // 1/10
}
```

## 添加图片

```json
{
  "header": {
    "left": {
      "type": "image",
      "path": "logo.png",
      "width": 60,
      "height": 30
    }
  }
}
```

---

**上一页**：[其他元素](../02-user-guide/elements/others.md)  
**下一页**：[自动目录](./table-of-contents.md)

