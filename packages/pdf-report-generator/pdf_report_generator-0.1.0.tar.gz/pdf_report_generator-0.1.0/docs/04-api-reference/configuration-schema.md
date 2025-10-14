# 配置Schema

完整的JSON Schema参考。

## Schema文件位置

`templates/template_schema.json`

## 使用Schema验证

### Python验证

```python
import json
import jsonschema

with open('templates/template_schema.json') as f:
    schema = json.load(f)

with open('my_config.json') as f:
    config = json.load(f)

try:
    jsonschema.validate(config, schema)
    print("✅ 配置有效")
except jsonschema.ValidationError as e:
    print(f"❌ 配置错误: {e.message}")
```

### VS Code集成

在配置文件顶部添加：

```json
{
  "$schema": "./templates/template_schema.json",
  "metadata": {...}
}
```

## 主要Schema部分

- metadata: 元数据配置
- styles: 样式定义
- coverPage: 封面配置
- toc: 目录配置
- pageTemplate: 页眉页脚
- dataSources: 数据源
- elements: 元素列表

---

**上一页**：[Web API](./web-api.md)  
**下一页**：[示例库](../05-examples/)

