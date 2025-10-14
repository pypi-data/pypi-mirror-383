# Web API

FastAPI REST接口完整文档。

## 启动API服务

```bash
python run_api.py
# 或
uvicorn api.main:app --reload
```

访问API文档：`http://localhost:8000/docs`

## API端点

### 生成PDF

**POST** `/api/v1/generate`

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"title": "测试报告"},
    "elements": [{"type": "text", "content": "Hello"}]
  }' \
  --output report.pdf
```

### 上传配置文件

**POST** `/api/v1/generate/upload`

```bash
curl -X POST "http://localhost:8000/api/v1/generate/upload" \
  -F "file=@config.json" \
  --output report.pdf
```

### 验证配置

**POST** `/api/v1/validate`

```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{"metadata": {...}}'
```

### 健康检查

**GET** `/api/v1/health`

```bash
curl http://localhost:8000/api/v1/health
```

## Python客户端示例

```python
import requests

config = {
    "metadata": {"title": "报告"},
    "elements": [{"type": "text", "content": "内容"}]
}

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json=config
)

with open("output.pdf", "wb") as f:
    f.write(response.content)
```

---

**上一页**：[Python API](./python-api/)  
**下一页**：[配置Schema](./configuration-schema.md)

