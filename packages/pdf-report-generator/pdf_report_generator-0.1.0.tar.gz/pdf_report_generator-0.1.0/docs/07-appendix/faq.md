# 常见问题解答（FAQ）

## 安装和配置

### Q: 如何安装依赖？

```bash
pip install -r requirements.txt
```

### Q: 中文显示为方框？

确保使用中文字体：

```json
{
  "styles": {
    "MyStyle": {
      "fontName": "SimHei"  // 或 SimSun, GB2312
    }
  }
}
```

### Q: matplotlib中文显示问题？

清除缓存：

```bash
rm -rf ~/.matplotlib
```

## 使用问题

### Q: 数据源找不到？

检查路径和数据源名称：

```json
{
  "dataSources": [{"name": "sales", "type": "csv", "path": "data/sales.csv"}],
  "elements": [{"type": "table", "dataSource": "sales"}]  // 名称要匹配
}
```

### Q: 图表不显示？

确保：
1. 数据源正确加载
2. 列名存在于数据中
3. 数据类型正确（数值型）

### Q: 页眉页脚不显示？

检查配置：

```json
{
  "pageTemplate": {
    "header": {
      "enabled": true,  // 必须启用
      "center": {"type": "text", "content": "内容"}
    }
  }
}
```

### Q: 目录是空白的？

确保：
1. `toc.enabled` 为 true
2. `toc.autoGenerate` 为 true
3. 文档中有 `heading` 元素

## 性能问题

### Q: 生成速度慢？

- 减少图表数量
- 降低图片分辨率
- 分批生成大型报告

### Q: 内存占用高？

- 处理大数据时分块读取
- 及时释放不用的变量

## API问题

### Q: API启动失败？

检查端口占用：

```bash
lsof -i :8000
```

### Q: CORS错误？

配置CORS：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)
```

## 更多帮助

- [故障排查](../06-development/troubleshooting.md)
- [GitHub Issues](https://github.com/your-org/pdf-report/issues)

---

**上一页**：[配置Schema](../04-api-reference/configuration-schema.md)  
**下一页**：[术语表](./glossary.md)

