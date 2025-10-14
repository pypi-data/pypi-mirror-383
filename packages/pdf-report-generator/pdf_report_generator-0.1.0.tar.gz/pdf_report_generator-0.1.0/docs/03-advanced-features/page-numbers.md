# 页码格式

页码格式定制指南。

## 页码格式

### 阿拉伯数字（默认）

```json
{
  "type": "pageNumber",
  "format": "{page}"  // 1, 2, 3...
}
```

### 罗马数字

```json
{
  "format": "{roman}"  // i, ii, iii...
}
```

### 中文数字

```json
{
  "format": "{chinese}"  // 一, 二, 三...
}
```

## 自定义格式

```json
{
  "format": "第 {page} 页"           // 第 1 页
  "format": "{page}/{total}"         // 1/10
  "format": "- {page} -"             // - 1 -
  "format": "Page {page} of {total}" // Page 1 of 10
}
```

---

**上一页**：[图片处理](./images-handling.md)  
**下一页**：[书签和链接](./bookmarks-links.md)

