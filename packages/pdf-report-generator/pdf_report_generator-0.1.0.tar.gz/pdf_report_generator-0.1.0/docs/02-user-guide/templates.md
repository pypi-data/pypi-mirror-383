# 模板变量

PDF报告生成器使用Jinja2模板引擎，支持在配置文件中使用动态变量和表达式。

## 基本语法

### 变量输出

使用双花括号输出变量：

```json
{
  "content": "报告日期：{{date}}"
}
```

### 表达式

```json
{
  "content": "总和：{{ 100 + 200 }}"
}
```

## 内置变量

### 日期和时间变量

| 变量 | 说明 | 示例输出 |
|------|------|----------|
| `{{date}}` | 当前日期 | 2024-03-15 |
| `{{datetime}}` | 当前日期时间 | 2024-03-15 14:30 |
| `{{year}}` | 当前年份 | 2024 |
| `{{month}}` | 当前月份 | 3 |
| `{{day}}` | 当前日期 | 15 |

### 页码变量

| 变量 | 说明 | 使用位置 |
|------|------|----------|
| `{{page}}` | 当前页码 | 页眉页脚 |
| `{{total}}` | 总页数 | 页眉页脚 |

### 元数据变量

访问配置中的元数据：

```json
{
  "metadata": {
    "title": "销售报告",
    "author": "张三",
    "company": "ABC公司"
  },
  "elements": [
    {
      "type": "text",
      "content": "标题：{{metadata.title}}"
    },
    {
      "type": "text",
      "content": "作者：{{metadata.author}}"
    }
  ]
}
```

### 数据源变量

访问数据源中的数据：

```json
{
  "dataSources": [
    {
      "name": "sales",
      "type": "inline",
      "data": [{"total": 1000000}]
    }
  ],
  "elements": [
    {
      "type": "text",
      "content": "总销售额：{{dataSources.sales[0].total}}"
    }
  ]
}
```

## 条件语句

### if语句

```json
{
  "content": "{% if metadata.urgent %}【紧急】{% endif %}{{metadata.title}}"
}
```

### if-else语句

```json
{
  "content": "{% if total > 1000000 %}优秀{% else %}良好{% endif %}"
}
```

### if-elif-else语句

```json
{
  "content": "{% if score >= 90 %}优秀{% elif score >= 80 %}良好{% elif score >= 60 %}及格{% else %}不及格{% endif %}"
}
```

### 条件示例

```json
{
  "metadata": {
    "reportType": "urgent"
  },
  "elements": [
    {
      "type": "text",
      "content": "{% if metadata.reportType == 'urgent' %}⚠️ 紧急报告{% else %}📄 常规报告{% endif %}",
      "style": "Title"
    }
  ]
}
```

## 循环语句

### for循环

```json
{
  "type": "text",
  "content": "{% for item in items %}• {{item}}\n{% endfor %}"
}
```

### 带索引的循环

```json
{
  "content": "{% for i, item in enumerate(items) %}{{i+1}}. {{item}}\n{% endfor %}"
}
```

### 循环示例

```json
{
  "dataSources": [
    {
      "name": "products",
      "type": "inline",
      "data": [
        {"name": "产品A", "price": 100},
        {"name": "产品B", "price": 150}
      ]
    }
  ],
  "elements": [
    {
      "type": "text",
      "content": "{% for product in dataSources.products %}• {{product.name}}: ¥{{product.price}}\n{% endfor %}"
    }
  ]
}
```

## 过滤器

### 文本过滤器

```json
{
  "content": "{{metadata.title | upper}}"      // 转大写
  "content": "{{metadata.title | lower}}"      // 转小写
  "content": "{{metadata.title | title}}"      // 首字母大写
  "content": "{{metadata.title | capitalize}}" // 句首字母大写
}
```

### 数字过滤器

```json
{
  "content": "{{price | round(2)}}"           // 保留2位小数
  "content": "{{number | abs}}"               // 绝对值
  "content": "{{value | int}}"                // 转整数
  "content": "{{value | float}}"              // 转浮点数
}
```

### 格式化过滤器

```json
{
  "content": "{{amount | format('%.2f')}}"    // 格式化数字
  "content": "{{text | truncate(50)}}"        // 截断文本
  "content": "{{text | wordwrap(40)}}"        // 文本换行
}
```

### 日期过滤器

```python
# 在Python中自定义过滤器
def date_format(value, format='%Y-%m-%d'):
    return value.strftime(format)

# 注册过滤器
config_parser.env.filters['dateformat'] = date_format
```

```json
{
  "content": "{{current_date | dateformat('%Y年%m月%d日')}}"
}
```

## 函数和表达式

### 数学运算

```json
{
  "content": "总计：{{ price * quantity }}"
  "content": "平均值：{{ total / count }}"
  "content": "增长率：{{ (new - old) / old * 100 }}%"
}
```

### 字符串操作

```json
{
  "content": "{{ 'Hello ' + name }}"          // 字符串连接
  "content": "{{ text.replace('old', 'new') }}" // 字符串替换
  "content": "{{ text.strip() }}"             // 去除空格
}
```

### 列表操作

```json
{
  "content": "数量：{{ items | length }}"      // 列表长度
  "content": "第一项：{{ items | first }}"     // 第一个元素
  "content": "最后一项：{{ items | last }}"    // 最后一个元素
}
```

## 高级用法

### 嵌套变量访问

```json
{
  "metadata": {
    "company": {
      "name": "ABC公司",
      "address": {
        "city": "北京",
        "district": "朝阳区"
      }
    }
  },
  "elements": [
    {
      "type": "text",
      "content": "公司地址：{{metadata.company.address.city}}{{metadata.company.address.district}}"
    }
  ]
}
```

### 默认值

```json
{
  "content": "{{metadata.subtitle | default('无副标题')}}"
}
```

### 变量赋值

```json
{
  "content": "{% set total = 1000 %}总额：{{total}}"
}
```

### 宏定义

```json
{
  "content": "{% macro price_tag(price) %}¥{{ '%.2f' % price }}{% endmacro %}{{ price_tag(100) }}"
}
```

## 实用示例

### 动态标题

```json
{
  "metadata": {
    "year": "2024",
    "quarter": "Q1",
    "department": "销售部"
  },
  "elements": [
    {
      "type": "heading",
      "text": "{{metadata.year}}年{{metadata.quarter}}{{metadata.department}}业绩报告",
      "level": 1
    }
  ]
}
```

### 条件样式

```json
{
  "dataSources": [
    {
      "name": "performance",
      "type": "inline",
      "data": [{"score": 95}]
    }
  ],
  "elements": [
    {
      "type": "text",
      "content": "{% if dataSources.performance[0].score >= 90 %}✅ 优秀{% elif dataSources.performance[0].score >= 60 %}⚠️ 合格{% else %}❌ 不合格{% endif %}",
      "style": "{% if dataSources.performance[0].score >= 90 %}SuccessText{% else %}WarningText{% endif %}"
    }
  ]
}
```

### 动态列表

```json
{
  "dataSources": [
    {
      "name": "highlights",
      "type": "inline",
      "data": [
        {"item": "销售额增长15%"},
        {"item": "新客户数量增加200"},
        {"item": "客户满意度提升至92%"}
      ]
    }
  ],
  "elements": [
    {
      "type": "text",
      "content": "主要亮点：\n{% for highlight in dataSources.highlights %}• {{highlight.item}}\n{% endfor %}"
    }
  ]
}
```

### 数据汇总

```json
{
  "content": "{% set total = 0 %}{% for item in data %}{% set total = total + item.amount %}{% endfor %}总计：{{total}}"
}
```

### 格式化数字

```json
{
  "content": "销售额：¥{{ '{:,.2f}'.format(amount) }}"
}
```

输出：`销售额：¥1,000,000.00`

## Python代码中使用模板

### 传递自定义变量

```python
from pdf_generator import PDFReportGenerator

# 准备变量
context = {
    "company": "ABC公司",
    "author_name": "张三",
    "report_date": "2024-03-15",
    "custom_data": {
        "total_sales": 1000000,
        "growth_rate": 0.15
    }
}

# 在配置中使用
config = {
    "elements": [
        {
            "type": "text",
            "content": "{{company}} - {{author_name}}"
        },
        {
            "type": "text",
            "content": "销售额：{{custom_data.total_sales}}"
        }
    ]
}

# 生成PDF
generator = PDFReportGenerator(config_dict=config)
# 注意：需要在ConfigParser中传递context
```

### 自定义过滤器

```python
from pdf_generator.config.parser import ConfigParser

parser = ConfigParser(config_dict=config)

# 注册自定义过滤器
def currency_format(value):
    return f"¥{value:,.2f}"

parser.env.filters['currency'] = currency_format
```

使用：

```json
{
  "content": "总额：{{amount | currency}}"
}
```

### 自定义函数

```python
def calculate_profit(sales, cost):
    return sales - cost

parser.env.globals['calculate_profit'] = calculate_profit
```

使用：

```json
{
  "content": "利润：{{calculate_profit(sales, cost)}}"
}
```

## 模板调试

### 显示变量值

```json
{
  "content": "调试：{{ metadata }}"  // 输出整个对象
}
```

### 检查变量类型

```json
{
  "content": "类型：{{ metadata.__class__.__name__ }}"
}
```

### 列出所有属性

```json
{
  "content": "{% for key in metadata.keys() %}{{key}}: {{metadata[key]}}\n{% endfor %}"
}
```

## 安全考虑

### 避免注入

```python
# ❌ 不安全
user_input = "<script>alert('xss')</script>"
config = {
    "content": f"{{{{user_input}}}}"
}

# ✅ 安全
config = {
    "content": "{{user_input | e}}"  // 转义HTML
}
```

### 限制模板功能

```python
from jinja2 import Environment, select_autoescape

env = Environment(
    autoescape=select_autoescape(['html', 'xml']),
    # 禁用某些功能
)
```

## 最佳实践

### 1. 保持简洁

```json
// ✅ 好的做法
{
  "content": "{{metadata.title}}"
}

// ❌ 避免过于复杂
{
  "content": "{% for i in range(10) %}{% if i > 5 %}{{i}}{% endif %}{% endfor %}"
}
```

### 2. 使用有意义的变量名

```json
{
  "metadata": {
    "reportTitle": "销售报告",    // ✅ 清晰
    "t": "销售报告"              // ❌ 不清晰
  }
}
```

### 3. 提供默认值

```json
{
  "content": "{{metadata.subtitle | default('无标题')}}"
}
```

### 4. 注释模板逻辑

```json
{
  "content": "{# 这里显示条件文本 #}{% if condition %}文本{% endif %}"
}
```

## 常见问题

### Q: 变量不显示？

检查变量路径是否正确：

```json
// ❌ 错误
{
  "content": "{{title}}"
}

// ✅ 正确
{
  "content": "{{metadata.title}}"
}
```

### Q: 如何在模板中使用数组？

```json
{
  "content": "{{items[0]}}"           // 访问第一个元素
  "content": "{{items | length}}"     // 数组长度
}
```

### Q: 日期格式化？

```python
# 在Python中处理
from datetime import datetime

context = {
    "report_date": datetime.now().strftime('%Y年%m月%d日')
}
```

## 下一步

- **[文本元素](./elements/text.md)** - 在文本中使用模板
- **[页眉页脚](../03-advanced-features/headers-footers.md)** - 页眉页脚中的变量
- **[封面页](../03-advanced-features/cover-pages.md)** - 封面中的动态内容

---

**上一页**：[样式系统](./styles.md)  
**下一页**：[文本元素](./elements/text.md)

