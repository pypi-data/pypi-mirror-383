# 数据源详解

PDF报告生成器支持多种数据源类型，本文档详细介绍每种数据源的配置和使用方法。

## 数据源概述

### 支持的数据源类型

- **CSV文件** - 逗号分隔值文件
- **JSON文件** - JSON格式数据
- **Excel文件** - .xlsx, .xls文件
- **HTTP API** - REST API接口
- **数据库** - SQL数据库
- **内联数据** - 直接在配置中定义数据

### 数据源配置结构

```json
{
  "dataSources": [
    {
      "name": "数据源名称",
      "type": "类型",
      ...其他配置
    }
  ]
}
```

## CSV数据源

### 基本配置

```json
{
  "dataSources": [
    {
      "name": "sales_data",
      "type": "csv",
      "path": "data/sales.csv"
    }
  ]
}
```

### 完整配置选项

```json
{
  "name": "sales_data",
  "type": "csv",
  "path": "data/sales.csv",
  "encoding": "utf-8",        // 文件编码
  "delimiter": ",",            // 分隔符
  "skiprows": 0,              // 跳过行数
  "usecols": ["列1", "列2"],  // 使用的列
  "na_values": ["N/A", "-"]   // 空值表示
}
```

### 示例数据文件

`sales.csv`:
```csv
月份,销售额,成本,利润
一月,450000,280000,170000
二月,520000,310000,210000
三月,580000,340000,240000
```

### 在元素中使用

```json
{
  "type": "table",
  "dataSource": "sales_data"
}
```

## JSON数据源

### 基本配置

```json
{
  "dataSources": [
    {
      "name": "products",
      "type": "json",
      "path": "data/products.json"
    }
  ]
}
```

### 使用JSON路径

```json
{
  "name": "products",
  "type": "json",
  "path": "data/api_response.json",
  "jsonPath": "$.data.products"
}
```

### JSON路径语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `$` | 根对象 | `$` |
| `.` | 子元素 | `$.data` |
| `[]` | 数组元素 | `$.products[0]` |
| `*` | 通配符 | `$.products[*].name` |
| `..` | 递归下降 | `$..price` |

### 示例JSON文件

`products.json`:
```json
{
  "data": {
    "products": [
      {"name": "产品A", "price": 100, "stock": 50},
      {"name": "产品B", "price": 150, "stock": 30}
    ]
  }
}
```

## Excel数据源

### 基本配置

```json
{
  "dataSources": [
    {
      "name": "budget",
      "type": "excel",
      "path": "data/budget.xlsx"
    }
  ]
}
```

### 指定工作表

```json
{
  "name": "budget",
  "type": "excel",
  "path": "data/budget.xlsx",
  "sheet": "2024年预算"  // 工作表名称或索引
}
```

### 完整配置

```json
{
  "name": "budget",
  "type": "excel",
  "path": "data/budget.xlsx",
  "sheet": "Sheet1",
  "skiprows": 1,           // 跳过标题行
  "usecols": "A:F",        // 使用A到F列
  "header": 0,             // 标题行索引
  "na_values": [""]        // 空值
}
```

### 列范围语法

```json
"usecols": "A:F"          // A到F列
"usecols": "A,C,E"        // A、C、E列
"usecols": [0, 2, 4]      // 第1、3、5列（索引从0开始）
```

## HTTP API数据源

### GET请求

```json
{
  "dataSources": [
    {
      "name": "api_sales",
      "type": "api",
      "url": "https://api.example.com/sales",
      "method": "GET",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  ]
}
```

### POST请求

```json
{
  "name": "api_data",
  "type": "api",
  "url": "https://api.example.com/query",
  "method": "POST",
  "headers": {
        "Content-Type": "application/json",
    "Authorization": "Bearer TOKEN"
  },
  "data": {
    "query": "sales",
    "year": 2024
  }
}
```

### 请求参数

```json
{
  "name": "api_search",
  "type": "api",
  "url": "https://api.example.com/search",
  "method": "GET",
  "params": {
    "q": "product",
    "limit": 100
  }
}
```

### 处理API响应

#### 提取嵌套数据

```json
{
  "name": "api_products",
  "type": "api",
  "url": "https://api.example.com/products",
  "jsonPath": "$.data.items"
}
```

#### 响应示例

```json
{
  "status": "success",
  "data": {
    "items": [
      {"id": 1, "name": "产品A"},
      {"id": 2, "name": "产品B"}
    ]
  }
}
```

使用 `jsonPath: "$.data.items"` 提取items数组。

### 认证方式

#### Bearer Token

```json
{
  "headers": {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
  }
}
```

#### API Key

```json
{
  "headers": {
    "X-API-Key": "YOUR_API_KEY"
  }
}
```

#### Basic Auth

```json
{
  "headers": {
    "Authorization": "Basic BASE64_ENCODED_CREDENTIALS"
  }
}
```

## 数据库数据源

### SQLite

```json
{
  "dataSources": [
    {
      "name": "db_sales",
      "type": "database",
      "connection": "sqlite:///data/sales.db",
      "query": "SELECT * FROM sales WHERE year = 2024"
    }
  ]
}
```

### PostgreSQL

```json
{
  "name": "pg_data",
  "type": "database",
  "connection": "postgresql://user:password@localhost:5432/mydb",
  "query": "SELECT product, sum(amount) as total FROM orders GROUP BY product"
}
```

### MySQL

```json
{
  "name": "mysql_data",
  "type": "database",
  "connection": "mysql+pymysql://user:password@localhost:3306/mydb",
  "query": "SELECT * FROM customers WHERE status = 'active'"
}
```

### SQL Server

```json
{
  "name": "mssql_data",
  "type": "database",
  "connection": "mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+17+for+SQL+Server",
  "query": "SELECT * FROM Sales"
}
```

### 参数化查询

```json
{
  "name": "filtered_data",
  "type": "database",
  "connection": "sqlite:///sales.db",
  "query": "SELECT * FROM sales WHERE year = :year AND month = :month",
  "params": {
    "year": 2024,
    "month": "Q1"
  }
}
```

## 内联数据源

### 列表格式

```json
{
  "dataSources": [
    {
      "name": "summary",
      "type": "inline",
      "data": [
        {"指标": "总销售额", "值": "¥1,000,000"},
        {"指标": "增长率", "值": "15%"},
        {"指标": "客户数", "值": "1,250"}
      ]
    }
  ]
}
```

### 字典格式

```json
{
  "name": "metrics",
  "type": "inline",
  "data": {
    "总销售额": 1000000,
    "增长率": 0.15,
    "客户数": 1250
  }
}
```

## 数据转换

### 使用Python代码添加数据

```python
from pdf_generator import PDFReportGenerator
import pandas as pd

# 创建DataFrame
df = pd.DataFrame({
    '产品': ['A', 'B', 'C'],
    '销量': [100, 150, 200]
})

# 创建生成器
generator = PDFReportGenerator(config_path="config.json")

# 添加数据源
generator.add_data_source("sales_data", df)

# 生成PDF
generator.save("output.pdf")
```

### 数据预处理

```python
import pandas as pd

# 读取数据
df = pd.read_csv("raw_data.csv")

# 数据清洗
df = df.dropna()  # 删除空值
df['金额'] = df['金额'].astype(float)  # 转换类型

# 数据计算
df['利润'] = df['销售额'] - df['成本']

# 添加到生成器
generator.add_data_source("processed_data", df)
```

## 数据源高级用法

### 多数据源合并

```python
import pandas as pd

# 加载多个数据源
sales = pd.read_csv("sales.csv")
costs = pd.read_csv("costs.csv")

# 合并数据
merged = pd.merge(sales, costs, on='产品')
merged['利润'] = merged['销售额'] - merged['成本']

# 添加到生成器
generator.add_data_source("profit_analysis", merged)
```

### 数据聚合

```python
# 按类别聚合
grouped = df.groupby('类别').agg({
    '销售额': 'sum',
    '数量': 'sum'
}).reset_index()

generator.add_data_source("category_summary", grouped)
```

### 数据筛选

```python
# 筛选2024年数据
filtered = df[df['年份'] == 2024]

# 筛选销售额大于10000的记录
high_sales = df[df['销售额'] > 10000]

generator.add_data_source("filtered_data", filtered)
```

## 错误处理

### 文件不存在

```json
{
  "name": "data",
  "type": "csv",
  "path": "data/missing.csv",
  "onError": "skip"  // skip, raise, default
}
```

### API超时

```json
{
  "name": "api_data",
  "type": "api",
  "url": "https://slow-api.com/data",
  "timeout": 30,  // 秒
  "retries": 3
}
```

### 数据库连接失败

```python
try:
    generator = PDFReportGenerator(config_path="config.json")
    generator.save("output.pdf")
except Exception as e:
    print(f"数据源错误: {e}")
```

## 性能优化

### 大数据集处理

```python
# 分块读取大文件
chunks = pd.read_csv("large_file.csv", chunksize=10000)

# 处理每个块
for chunk in chunks:
    # 处理数据
    processed = process_chunk(chunk)
    # 生成报告
    ...
```

### 缓存数据

```python
import pickle

# 保存处理后的数据
df = pd.read_csv("data.csv")
processed = preprocess(df)
processed.to_pickle("cached_data.pkl")

# 下次直接加载
df = pd.read_pickle("cached_data.pkl")
```

### 数据库索引

```sql
-- 在数据库中创建索引以加速查询
CREATE INDEX idx_year ON sales(year);
CREATE INDEX idx_product ON sales(product_id);
```

## 安全考虑

### 敏感信息保护

```python
# 使用环境变量存储凭证
import os

config = {
  "dataSources": [{
    "name": "secure_api",
    "type": "api",
    "url": os.getenv("API_URL"),
    "headers": {
      "Authorization": f"Bearer {os.getenv('API_TOKEN')}"
    }
  }]
}
```

### SQL注入防护

```python
# ❌ 不安全的做法
query = f"SELECT * FROM users WHERE id = {user_input}"

# ✅ 安全的做法
query = "SELECT * FROM users WHERE id = :id"
params = {"id": user_input}
```

## 常见问题

### Q: 如何处理中文编码问题？

```json
{
  "type": "csv",
  "path": "data.csv",
  "encoding": "gbk"  // 或 "utf-8-sig" (带BOM的UTF-8)
}
```

### Q: Excel日期格式问题？

```python
df = pd.read_excel("data.xlsx")
df['日期'] = pd.to_datetime(df['日期'])
```

### Q: API返回的数据格式不一致？

```python
def normalize_api_data(response):
    if isinstance(response, list):
        return pd.DataFrame(response)
    elif isinstance(response, dict):
        return pd.DataFrame([response])
    else:
        raise ValueError("未知数据格式")
```

## 下一步

- **[样式系统](./styles.md)** - 学习样式定制
- **[表格元素](./elements/table.md)** - 使用数据创建表格
- **[图表元素](./elements/chart.md)** - 数据可视化

---

**上一页**：[配置文件总览](./configuration-overview.md)  
**下一页**：[样式系统](./styles.md)

