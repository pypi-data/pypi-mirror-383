# 创建第一个完整报告

本教程将指导您创建一个包含封面、目录、页眉页脚、表格和图表的完整专业报告。

## 教程目标

创建一个"2024年第一季度销售分析报告"，包含：

- ✅ 精美的封面页
- ✅ 自动生成的目录
- ✅ 页眉和页脚
- ✅ 多级标题结构
- ✅ 数据表格
- ✅ 可视化图表
- ✅ 格式化文本

## 第一步：准备数据

### 创建销售数据文件

创建 `q1_sales_data.csv`：

```csv
月份,销售额,成本,利润,客户数
一月,450000,280000,170000,125
二月,520000,310000,210000,148
三月,580000,340000,240000,167
```

### 创建产品数据文件

创建 `products.json`：

```json
{
  "products": [
    {
      "name": "智能手机",
      "q1_sales": 1850000,
      "growth": "+18%"
    },
    {
      "name": "平板电脑",
      "q1_sales": 980000,
      "growth": "+12%"
    },
    {
      "name": "智能手表",
      "q1_sales": 680000,
      "growth": "+25%"
    },
    {
      "name": "无线耳机",
      "q1_sales": 420000,
      "growth": "+32%"
    }
  ]
}
```

## 第二步：创建配置文件

创建 `complete_report_config.json`：

```json
{
  "metadata": {
    "title": "2024年第一季度销售分析报告",
    "author": "销售分析部",
    "company": "科技有限公司",
    "pageSize": "A4"
  },
  
  "coverPage": {
    "enabled": true,
    "background": {
      "type": "gradient",
      "colorStart": "#1e3c72",
      "colorEnd": "#2a5298"
    },
    "elements": [
      {
        "type": "text",
        "content": "{{metadata.title}}",
        "style": "Title",
        "position": {"x": "center", "y": 550}
      },
      {
        "type": "text",
        "content": "{{metadata.company}}",
        "style": "Heading1",
        "position": {"x": "center", "y": 450}
      },
      {
        "type": "text",
        "content": "编制部门：{{metadata.author}}",
        "style": "Normal",
        "position": {"x": "center", "y": 250}
      },
      {
        "type": "text",
        "content": "{{date}}",
        "style": "Normal",
        "position": {"x": "center", "y": 200}
      }
    ]
  },
  
  "toc": {
    "enabled": true,
    "autoGenerate": true,
    "title": "目  录",
    "maxLevel": 2
  },
  
  "pageTemplate": {
    "header": {
      "enabled": true,
      "height": 0.8,
      "showLine": true,
      "left": {
        "type": "text",
        "content": "{{metadata.title}}"
      },
      "right": {
        "type": "text",
        "content": "{{date}}"
      }
    },
    "footer": {
      "enabled": true,
      "height": 0.6,
      "showLine": true,
      "center": {
        "type": "pageNumber",
        "format": "第 {page} 页 共 {total} 页"
      }
    }
  },
  
  "dataSources": [
    {
      "name": "monthly_sales",
      "type": "csv",
      "path": "q1_sales_data.csv"
    },
    {
      "name": "products",
      "type": "json",
      "path": "products.json",
      "jsonPath": "$.products"
    }
  ],
  
  "elements": [
    {
      "type": "heading",
      "text": "第一章 报告概述",
      "level": 1
    },
    {
      "type": "text",
      "content": "本报告全面分析了2024年第一季度的销售业绩，包括月度销售趋势、产品表现和市场洞察。报告旨在为管理层提供决策依据，优化第二季度的销售策略。",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 20
    },
    {
      "type": "heading",
      "text": "1.1 关键发现",
      "level": 2
    },
    {
      "type": "text",
      "content": "• 第一季度总销售额达到 ¥155万元，同比增长15%\n• 三月份销售额创新高，达到 ¥58万元\n• 智能手表增长最快，增长率达32%\n• 新增客户440人，客户留存率提升至87%",
      "style": "BodyText"
    },
    {
      "type": "pageBreak"
    },
    {
      "type": "heading",
      "text": "第二章 月度销售分析",
      "level": 1
    },
    {
      "type": "heading",
      "text": "2.1 月度销售数据",
      "level": 2
    },
    {
      "type": "text",
      "content": "下表展示了第一季度各月的销售额、成本、利润和客户数据：",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 10
    },
    {
      "type": "table",
      "dataSource": "monthly_sales",
      "style": {
        "gridColor": "#CCCCCC",
        "headerBackgroundColor": "#4472C4",
        "headerTextColor": "#FFFFFF",
        "alternateRowColor": "#F2F2F2",
        "fontSize": 10,
        "alignment": "center"
      }
    },
    {
      "type": "spacer",
      "height": 20
    },
    {
      "type": "heading",
      "text": "2.2 销售趋势图",
      "level": 2
    },
    {
      "type": "text",
      "content": "从下图可以看出，销售额呈现稳定增长趋势，三月份达到季度峰值：",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 10
    },
    {
      "type": "chart",
      "chartType": "line",
      "dataSource": "monthly_sales",
      "xColumn": "月份",
      "yColumns": ["销售额", "成本", "利润"],
      "title": "第一季度销售趋势",
      "width": 450,
      "height": 300,
      "showLegend": true,
      "colors": ["#4472C4", "#ED7D31", "#70AD47"]
    },
    {
      "type": "pageBreak"
    },
    {
      "type": "heading",
      "text": "第三章 产品分析",
      "level": 1
    },
    {
      "type": "heading",
      "text": "3.1 产品销售表现",
      "level": 2
    },
    {
      "type": "text",
      "content": "各产品线在第一季度均实现了正增长，具体表现如下：",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 10
    },
    {
      "type": "table",
      "dataSource": "products",
      "columns": ["name", "q1_sales", "growth"],
      "style": {
        "gridColor": "#CCCCCC",
        "headerBackgroundColor": "#70AD47",
        "headerTextColor": "#FFFFFF",
        "alternateRowColor": "#E2EFDA",
        "alignment": "center"
      }
    },
    {
      "type": "spacer",
      "height": 20
    },
    {
      "type": "heading",
      "text": "3.2 产品销售额占比",
      "level": 2
    },
    {
      "type": "chart",
      "chartType": "pie",
      "dataSource": "products",
      "labelColumn": "name",
      "valueColumn": "q1_sales",
      "title": "产品销售额占比",
      "width": 400,
      "height": 300,
      "showLegend": true
    },
    {
      "type": "spacer",
      "height": 20
    },
    {
      "type": "heading",
      "text": "3.3 产品增长对比",
      "level": 2
    },
    {
      "type": "chart",
      "chartType": "bar",
      "dataSource": "products",
      "xColumn": "name",
      "yColumn": "q1_sales",
      "title": "各产品销售额对比",
      "width": 450,
      "height": 300,
      "colors": ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000"]
    },
    {
      "type": "pageBreak"
    },
    {
      "type": "heading",
      "text": "第四章 结论与建议",
      "level": 1
    },
    {
      "type": "heading",
      "text": "4.1 主要结论",
      "level": 2
    },
    {
      "type": "text",
      "content": "通过对第一季度销售数据的深入分析，我们得出以下结论：",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 10
    },
    {
      "type": "text",
      "content": "1. 整体销售形势良好，各项指标均超预期\n2. 智能手表和无线耳机成为新的增长点\n3. 客户获取和留存能力显著提升\n4. 利润率保持稳定，运营效率提高",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 20
    },
    {
      "type": "heading",
      "text": "4.2 第二季度建议",
      "level": 2
    },
    {
      "type": "text",
      "content": "基于第一季度的表现，建议第二季度采取以下策略：",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 10
    },
    {
      "type": "text",
      "content": "• 加大智能手表和无线耳机的营销投入\n• 优化供应链，降低成本，提高利润率\n• 推出客户忠诚度计划，进一步提升留存率\n• 开发新产品线，丰富产品组合",
      "style": "BodyText"
    },
    {
      "type": "spacer",
      "height": 30
    },
    {
      "type": "text",
      "content": "本报告完。",
      "style": "Normal",
      "alignment": "center"
    }
  ]
}
```

## 第三步：生成报告

创建 `generate_complete_report.py`：

```python
from pdf_generator import PDFReportGenerator

def main():
    print("开始生成完整报告...")
    
    # 加载配置并生成PDF
    generator = PDFReportGenerator(
        config_path="complete_report_config.json"
    )
    
    # 生成PDF文件
    output_file = "Q1_Sales_Analysis_Report.pdf"
    generator.save(output_file)
    
    print(f"✅ 报告生成成功：{output_file}")
    print("\n报告包含：")
    print("  - 封面页（渐变背景）")
    print("  - 自动生成的目录")
    print("  - 页眉和页脚")
    print("  - 4个章节，多级标题")
    print("  - 2个数据表格")
    print("  - 3个可视化图表")
    
    # 查看数据源摘要
    summary = generator.get_data_source_summary()
    print("\n数据源信息：")
    for name, info in summary.items():
        print(f"  - {name}: {info}")

if __name__ == "__main__":
    main()
```

### 运行生成脚本

```bash
python generate_complete_report.py
```

## 第四步：自定义和调整

### 调整封面样式

#### 使用纯色背景

```json
"coverPage": {
  "background": {
    "type": "color",
    "color": "#2E4053"
  }
}
```

#### 使用图片背景

```json
"coverPage": {
  "background": {
    "type": "image",
    "path": "cover_background.jpg",
    "opacity": 0.3
  }
}
```

### 调整页眉页脚

#### 添加公司Logo

```json
"pageTemplate": {
  "header": {
    "left": {
      "type": "image",
      "path": "company_logo.png",
      "width": 60,
      "height": 30
    },
    "right": {
      "type": "text",
      "content": "{{metadata.title}}"
    }
  }
}
```

#### 自定义页码格式

```json
"footer": {
  "center": {
    "type": "pageNumber",
    "format": "- {page} -"  // 阿拉伯数字
    // "format": "{roman}"   // 罗马数字
    // "format": "{chinese}" // 中文数字
  }
}
```

### 调整图表样式

#### 修改图表颜色

```json
{
  "type": "chart",
  "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"]
}
```

#### 调整图表大小

```json
{
  "type": "chart",
  "width": 500,   // 宽度（像素）
  "height": 350   // 高度（像素）
}
```

### 调整表格样式

```json
{
  "type": "table",
  "style": {
    "gridColor": "#DDDDDD",
    "headerBackgroundColor": "#2C3E50",
    "headerTextColor": "#FFFFFF",
    "alternateRowColor": "#ECF0F1",
    "fontSize": 9,
    "alignment": "left",
    "cellPadding": 8
  }
}
```

## 第五步：使用Python代码动态生成

### 编程方式创建配置

```python
from pdf_generator import PDFReportGenerator
import pandas as pd

# 准备数据
monthly_data = pd.DataFrame({
    '月份': ['一月', '二月', '三月'],
    '销售额': [450000, 520000, 580000],
    '成本': [280000, 310000, 340000],
    '利润': [170000, 210000, 240000]
})

# 动态构建配置
config = {
    "metadata": {
        "title": "销售分析报告",
        "author": "数据分析部"
    },
    "coverPage": {
        "enabled": True,
        "background": {"type": "color", "color": "#34495E"},
        "elements": [
            {
                "type": "text",
                "content": "销售分析报告",
                "style": "Title",
                "position": {"x": "center", "y": 500}
            }
        ]
    },
    "toc": {"enabled": True, "autoGenerate": True},
    "pageTemplate": {
        "header": {
            "enabled": True,
            "center": {"type": "text", "content": "销售分析报告"}
        },
        "footer": {
            "enabled": True,
            "center": {"type": "pageNumber", "format": "{page}"}
        }
    },
    "elements": []
}

# 添加内容元素
config["elements"].append({
    "type": "heading",
    "text": "销售数据分析",
    "level": 1
})

config["elements"].append({
    "type": "text",
    "content": "本报告分析了第一季度的销售数据。"
})

# 创建生成器并添加数据
generator = PDFReportGenerator(config_dict=config)
generator.add_data_source("monthly_sales", monthly_data)

# 添加表格元素
config["elements"].append({
    "type": "table",
    "dataSource": "monthly_sales"
})

# 生成PDF
generator.save("dynamic_report.pdf")
```

## 常见问题

### 问题1：封面文字位置不对

**原因**：Y坐标是从页面底部开始计算的。

**解决**：
- A4页面高度约为842点
- 顶部区域：y = 700-800
- 中部区域：y = 400-600
- 底部区域：y = 100-300

### 问题2：目录没有生成

**检查**：
1. 确保 `toc.enabled` 为 `true`
2. 确保 `toc.autoGenerate` 为 `true`
3. 确保有 `heading` 类型的元素

### 问题3：页眉页脚不显示

**检查**：
1. 确保 `pageTemplate.header.enabled` 为 `true`
2. 确保 `pageTemplate.footer.enabled` 为 `true`
3. 检查是否有内容配置（left/center/right）

### 问题4：图表显示异常

**解决**：
1. 确保数据源已正确加载
2. 检查列名是否正确
3. 确认数据类型（数值型数据）

## 完整示例下载

项目中包含完整示例：

```bash
# 查看高级功能示例
python examples/advanced_features_demo.py

# 将生成多个完整报告示例
```

## 下一步

恭喜！您已经掌握了创建完整专业报告的方法。接下来可以：

1. **[学习基本概念](../02-user-guide/basic-concepts.md)** - 深入理解系统原理
2. **[探索高级功能](../03-advanced-features/)** - 掌握更多高级特性
3. **[查看API参考](../04-api-reference/)** - 了解完整API
4. **[浏览更多示例](../05-examples/)** - 学习各种应用场景

## 参考资源

- **[配置文件总览](../02-user-guide/configuration-overview.md)** - 完整配置说明
- **[样式系统](../02-user-guide/styles.md)** - 自定义样式
- **[图表元素](../02-user-guide/elements/chart.md)** - 图表详解
- **[表格元素](../02-user-guide/elements/table.md)** - 表格详解

---

**上一页**：[快速开始](./quick-start.md)  
**下一页**：[部署指南](./deployment.md)

