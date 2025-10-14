# 中文字体

中文字体配置和使用指南。

## 默认中文字体

系统包含三种中文字体：
- **SimHei** - 黑体（默认）
- **SimSun** - 宋体
- **GB2312** - GB2312字体

## 使用中文字体

```json
{
  "styles": {
    "ChineseText": {
      "fontName": "SimHei",
      "fontSize": 12
    }
  }
}
```

## Matplotlib中文显示

系统自动配置Matplotlib中文支持，无需额外设置。

## 自定义字体

将TTF字体文件放入 `fonts/` 目录即可自动加载。

---

**上一页**：[表格合并](./table-merging.md)  
**下一页**：[图片处理](./images-handling.md)

