# 部署指南

本指南介绍如何在不同环境中部署PDF报告生成器，包括本地开发、服务器部署和Docker容器化部署。

## 部署架构

PDF报告生成器支持两种部署模式：

1. **库模式**：作为Python包集成到其他应用中
2. **服务模式**：独立的Web API服务

## 本地开发部署

### Python库模式

#### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd pdf-report-generator

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装为开发包
pip install -e .
```

#### 2. 在项目中使用

```python
from pdf_generator import PDFReportGenerator

# 直接在代码中使用
config = {...}
generator = PDFReportGenerator(config_dict=config)
generator.save("output.pdf")
```

### Web API服务模式

#### 1. 启动开发服务器

```bash
# 方式1：使用提供的启动脚本
python run_api.py

# 方式2：直接使用uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 验证服务

访问以下URL验证服务：

- **API文档**：`http://localhost:8000/docs`
- **健康检查**：`http://localhost:8000/api/v1/health`
- **ReDoc文档**：`http://localhost:8000/redoc`

#### 3. 开发环境配置

创建 `.env` 文件（可选）：

```env
# 服务配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# 文件上传限制
MAX_UPLOAD_SIZE=10485760  # 10MB

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 生产服务器部署

### 使用Gunicorn + Uvicorn

Gunicorn是生产级的WSGI服务器，配合Uvicorn Worker可以提供高性能的异步支持。

#### 1. 安装Gunicorn

```bash
pip install gunicorn
```

#### 2. 创建启动脚本

创建 `start_production.sh`：

```bash
#!/bin/bash

# 设置环境变量
export WORKERS=4
export HOST=0.0.0.0
export PORT=8000

# 启动Gunicorn
gunicorn api.main:app \
  --workers $WORKERS \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind $HOST:$PORT \
  --timeout 300 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info
```

#### 3. 赋予执行权限并启动

```bash
chmod +x start_production.sh
./start_production.sh
```

### 使用Nginx反向代理

#### 1. 安装Nginx

```bash
# Ubuntu/Debian
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 2. 配置Nginx

创建 `/etc/nginx/sites-available/pdf-generator`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 客户端最大上传大小
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置（PDF生成可能需要较长时间）
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # 静态文件（如果有）
    location /static {
        alias /path/to/pdf-generator/static;
    }
}
```

#### 3. 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/pdf-generator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 使用Systemd服务

创建 `/etc/systemd/system/pdf-generator.service`：

```ini
[Unit]
Description=PDF Report Generator API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/pdf-generator
Environment="PATH=/path/to/pdf-generator/venv/bin"
ExecStart=/path/to/pdf-generator/venv/bin/gunicorn \
    api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 300
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl enable pdf-generator
sudo systemctl start pdf-generator
sudo systemctl status pdf-generator
```

## Docker部署

### 创建Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 复制字体文件
COPY fonts/ /app/fonts/

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 启动命令
CMD ["gunicorn", "api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "300"]
```

### 创建docker-compose.yml

```yaml
version: '3.8'

services:
  pdf-generator:
    build: .
    container_name: pdf-generator
    ports:
      - "8000:8000"
    volumes:
      - ./fonts:/app/fonts:ro
      - ./data:/app/data:ro
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - DEBUG=false
      - MAX_UPLOAD_SIZE=20971520
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 可选：添加Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: pdf-generator-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - pdf-generator
    restart: unless-stopped
```

### 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Docker优化建议

#### 多阶段构建

```dockerfile
# 构建阶段
FROM python:3.10 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.10-slim
WORKDIR /app

# 复制依赖
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 安装字体
RUN apt-get update && \
    apt-get install -y fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/*

COPY . .
EXPOSE 8000
CMD ["gunicorn", "api.main:app", ...]
```

## 云平台部署

### AWS部署

#### 使用EC2

1. 启动EC2实例（推荐t3.medium或更高）
2. 安装Docker或Python环境
3. 按照上述服务器部署步骤操作
4. 配置安全组开放80/443端口

#### 使用ECS/Fargate

1. 推送Docker镜像到ECR
2. 创建ECS任务定义
3. 创建ECS服务
4. 配置ALB（Application Load Balancer）

#### 使用Lambda（无服务器）

由于PDF生成可能耗时较长，建议：
- 使用Lambda异步调用
- 配置较长的超时时间（最大15分钟）
- 结果保存到S3

### Azure部署

#### 使用Azure App Service

```bash
# 安装Azure CLI
az login

# 创建App Service
az webapp create \
  --name pdf-generator \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --runtime "PYTHON:3.10"

# 部署代码
az webapp up --name pdf-generator
```

### Google Cloud部署

#### 使用Cloud Run

```bash
# 构建并推送镜像
gcloud builds submit --tag gcr.io/PROJECT_ID/pdf-generator

# 部署到Cloud Run
gcloud run deploy pdf-generator \
  --image gcr.io/PROJECT_ID/pdf-generator \
  --platform managed \
  --region us-central1 \
  --timeout 300 \
  --memory 2Gi
```

## 性能优化

### Worker数量配置

```python
# 计算公式：(2 × CPU核心数) + 1
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
```

### 超时配置

PDF生成可能需要较长时间，建议配置：

- **Gunicorn timeout**：300秒（5分钟）
- **Nginx proxy timeout**：300秒
- **客户端timeout**：根据需求调整

### 内存优化

对于大型报告：

```python
# 在配置中启用流式处理（如果支持）
config = {
    "optimization": {
        "streaming": True,
        "chunk_size": 1000
    }
}
```

### 缓存策略

使用Redis缓存频繁生成的报告：

```python
import redis
import hashlib

redis_client = redis.Redis(host='localhost', port=6379)

def generate_with_cache(config):
    # 生成配置的哈希作为缓存键
    config_hash = hashlib.md5(
        json.dumps(config, sort_keys=True).encode()
    ).hexdigest()
    
    # 检查缓存
    cached = redis_client.get(config_hash)
    if cached:
        return cached
    
    # 生成PDF
    pdf_bytes = generator.to_bytes()
    
    # 保存到缓存（1小时过期）
    redis_client.setex(config_hash, 3600, pdf_bytes)
    
    return pdf_bytes
```

## 监控和日志

### 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
handler = RotatingFileHandler(
    'logs/pdf-generator.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

### 性能监控

使用Prometheus + Grafana：

```python
from prometheus_client import Counter, Histogram

# 定义指标
pdf_generated = Counter('pdf_generated_total', 'Total PDFs generated')
pdf_generation_time = Histogram('pdf_generation_seconds', 'PDF generation time')

# 在生成时记录
with pdf_generation_time.time():
    generator.save("output.pdf")
pdf_generated.inc()
```

## 安全配置

### HTTPS配置

使用Let's Encrypt免费SSL证书：

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### API安全

1. **API密钥认证**

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

2. **速率限制**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/generate")
@limiter.limit("10/minute")
async def generate_pdf(request: Request, config: dict):
    ...
```

## 备份和恢复

### 数据备份

```bash
# 备份配置和数据
tar -czf backup-$(date +%Y%m%d).tar.gz \
  templates/ \
  data/ \
  fonts/ \
  config/

# 定时备份（crontab）
0 2 * * * /path/to/backup.sh
```

### 容灾方案

1. **多区域部署**：在多个云区域部署服务
2. **负载均衡**：使用负载均衡器分发请求
3. **自动扩缩容**：根据负载自动调整实例数量

## 故障排查

### 常见部署问题

1. **端口被占用**
```bash
# 查找占用端口的进程
lsof -i :8000
# 或
netstat -tulpn | grep 8000
```

2. **权限问题**
```bash
# 检查文件权限
ls -l
# 修改权限
chmod +x start.sh
```

3. **内存不足**
```bash
# 查看内存使用
free -h
# 调整worker数量或增加内存
```

## 下一步

部署完成后，您可以：

1. **[查看API文档](../04-api-reference/web-api.md)** - 了解API使用方法
2. **[性能优化](../06-development/troubleshooting.md)** - 优化生产性能
3. **[监控指南](../06-development/troubleshooting.md)** - 设置监控和告警

---

**上一页**：[创建第一个完整报告](./first-report.md)  
**下一页**：[基本概念](../02-user-guide/basic-concepts.md)

