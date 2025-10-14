# 表格合并

表格单元格合并功能允许创建复杂的表格布局。

## 基本合并

```json
{
  "type": "table",
  "dataSource": "data",
  "mergeRules": [
    {
      "startRow": 0,
      "startCol": 0,
      "endRow": 0,
      "endCol": 1,
      "content": "合并单元格"
    }
  ]
}
```

## 合并规则

- startRow/startCol: 起始行列（从0开始）
- endRow/endCol: 结束行列
- content: 合并后显示的内容（可选）

## 示例

### 合并表头

```json
{
  "mergeRules": [
    {
      "startRow": 0,
      "startCol": 1,
      "endRow": 0,
      "endCol": 3,
      "content": "季度数据"
    }
  ]
}
```

### 合并行

```json
{
  "mergeRules": [
    {
      "startRow": 1,
      "startCol": 0,
      "endRow": 3,
      "endCol": 0,
      "content": "分类A"
    }
  ]
}
```

---

**上一页**：[封面设计](./cover-pages.md)  
**下一页**：[中文字体](./chinese-fonts.md)

