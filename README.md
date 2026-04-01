# 能源行业新闻爬虫

## 项目简介

一个支持多网站并发的能源行业新闻爬虫，专注于抓取和分析能源行业的政策新闻、技术新闻和微信公众号文章。该项目采用模块化设计，支持多线程并发抓取，具备智能过滤和去重功能，并集成了Qwen大模型进行文章价值分析，帮助用户快速获取有价值的行业信息。

## 主要功能

- **多模式支持**：政策新闻 (`zc`)、技术新闻 (`js`)、微信公众号 (`wechat`)
- **并发抓取**：支持多线程并发抓取，提高抓取效率
- **智能过滤**：支持按时间范围过滤文章
- **数据去重**：自动移除重复的文章
- **多种存储格式**：支持 CSV 格式存储
- **错误处理**：完善的错误处理和重试机制
- **微信公众号支持**：通过 API 抓取微信公众号文章
- **智能分析**：使用Qwen大模型分析文章价值并筛选
- **原文抓取**：自动抓取文章原文进行深度分析
- **规则过滤**：基于标题和来源的规则过滤

## 系统架构

### 核心组件

1. **爬虫模块**：负责从各个网站抓取文章，包括：
   - 基础爬虫类 (`base_spider.py`)
   - 各网站专用爬虫 (`*_spider.py`)
   - 微信公众号爬虫 (`wechat_spider.py`)

2. **工具模块**：提供各种辅助功能，包括：
   - 编码检测 (`encoding_detector.py`)
   - 日期解析 (`parse_date.py`)
   - 存储处理 (`storage_handler.py`)
   - 文章抓取 (`article_fetch.py`)
   - Qwen大模型分析 (`qwen_analyzer.py`)

3. **调度模块**：协调各个爬虫的运行，包括：
   - 爬虫调度器 (`crawler.py`)
   - 主入口 (`main.py`)

### 工作流程

1. **初始化**：加载配置，注册爬虫
2. **抓取**：多线程并发抓取文章
3. **过滤**：按时间范围过滤文章
4. **去重**：移除重复的文章
5. **存储**：保存到 CSV 文件
6. **分析**：（可选）使用Qwen大模型分析文章价值
7. **筛选**：（可选）根据分析结果筛选文章

## 常见问题

### 1. 微信公众号 API 如何获取 auth-key？

微信公众号 API 的 auth-key 需要通过第三方服务获取，具体获取方式请参考[wechat-article-exporter](https://docs.mptext.top/)的文档。

### 2. 为什么部分网站抓取失败？

可能的原因包括：
- 网站有反爬机制，限制了请求频率
- 网站结构发生变化，爬虫解析规则失效
- 网络连接问题
- 网站服务器暂时不可用

### 3. Qwen大模型分析功能如何获取 API 密钥？

需要在阿里云 DashScope 平台注册账号，创建 API 密钥。详细步骤请参考阿里云官方文档。

### 4. 如何提高抓取效率？

- 增加并发线程数：`--workers 5`
- 减少最大抓取页数：`--max_pages 3`
- 限制时间范围：`--time_limit 7`

### 5. 如何添加自定义规则过滤？

修改 `utils/qwen_analyzer.py` 文件中的 `filter_rules` 配置，添加自定义的标题关键词、来源黑名单等。

## 性能优化

1. **并发抓取**：使用多线程并发抓取，提高效率
2. **批量分析**：使用批量API调用，减少API调用次数
3. **缓存机制**：对已经抓取过的页面进行缓存
4. **错误重试**：对失败的请求进行有限次数的重试
5. **延迟控制**：合理设置请求间隔，避免触发反爬机制

## 未来计划

1. 增加更多能源行业相关网站
2. 支持更多存储格式（如 JSON、数据库）
3. 增加文章分类和标签功能
4. 实现定时抓取和自动分析
5. 开发可视化界面，方便用户操作
6. 增加更多大模型分析选项

## 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 致谢

- 感谢所有开源库的贡献者，感谢wechat-article-exporter项目提供的微信公众号接口
- 感谢阿里云提供的 Qwen 大模型服务
- 感谢各能源行业网站提供的优质内容

## 支持的网站

### 政策新闻模式 (`zc`)

- 北极星电力网 - 政策
- 中国能源新闻网 - 地方能源
- 储能中国网 - 政策
- 中国储能网 - 政策
- 国际电力网 - 政策
- 新能源网 - 政策
- 智能制造网 - 政策
- 中国核技术网 - 政策法规

### 技术新闻模式 (`js`)

- 北极星电力网 - 技术
- 中国能源新闻网 - 电力
- 中国能源新闻网 - 科技
- 储能中国网 - 技术
- 中国储能网 - 技术
- 中国电力企业联合会
- 南方电网能源观察
- 国际电力网 - 技术
- 新能源网 - 技术
- 全球氢能网
- 智能制造网 - 技术
- 国家核安全局
- 科学网 - 信息科学
- 科学网 - 工程
- 中国核技术网 - 技术装备
- 中国核技术网 - 产业应用

### 微信公众号模式 (`wechat`)

- 能源日参
- 中国能源观察
- 双碳情报
- 四新集团
- 国际能源小数据
- 能源新媒
- 青岛科技发展研究
- 九樟能参
- 维度系列
- 国际能源研究中心
- 生态环境部
- 国家能源局
- 落基山研究所
- 南方能源观察
- 中国电力报
- 中国能源报

## 安装指南

### 环境要求

- Python 3.7+
- pip

### 安装依赖

```bash
pip install requests beautifulsoup4
```

## 使用方法

### 基本命令

```bash
# 抓取政策新闻（最近 30 天，5 页）
python main.py zc

# 抓取技术新闻（最近 7 天）
python main.py js --time_limit 7

# 抓取微信公众号文章
python main.py wechat

# 抓取单个网站
python main.py solo --url "https://example.com"

# 抓取并使用Qwen大模型分析文章价值
python main.py zc --analyze --api_key YOUR_API_KEY
```

### 可选参数

- `--time_limit`：时间过滤器（天数），默认 30 天，0 表示不过滤
- `--output_dir`：输出目录，默认 `./output`
- `--max_pages`：最大抓取页数，默认 5 页
- `--timeout`：请求超时时间（秒），默认 30 秒
- `--retry`：重试次数，默认 3 次
- `--workers`：并发线程数，默认 3
- `--debug`：启用调试模式，输出详细日志
- `--analyze`：使用Qwen大模型分析文章价值并筛选
- `--api_key`：阿里云DashScope API密钥（用于Qwen大模型分析）
- `--threshold`：文章价值筛选阈值，高于此分数的文章会被保留，默认 5

### 微信公众号模式

运行微信公众号模式时，系统会提示输入微信 API 的 `auth-key`：

```bash
python main.py wechat
# 请输入微信API的auth-key: XXXXXXXXXXXXXXXXXXXXXXXXX
```

## 项目结构

```
web_crawler/
├── spiders/          # 爬虫实现
│   ├── __init__.py
│   ├── base_spider.py    # 爬虫基类
│   ├── bjx_spider.py     # 北极星电力网爬虫
│   ├── cpnn_spider.py    # 中国能源新闻网爬虫
│   ├── cnes_spider.py    # 储能中国网爬虫
│   ├── escn_spider.py    # 中国储能网爬虫
│   ├── cec_spider.py     # 中国电力企业联合会爬虫
│   ├── csg_spider.py     # 南方电网能源观察爬虫
│   ├── inen_spider.py    # 国际电力网爬虫
│   ├── nes_spider.py     # 新能源网爬虫
│   ├── hydroe_spider.py  # 全球氢能网爬虫
│   ├── gkzhan_spider.py  # 智能制造网爬虫
│   ├── nsa_spider.py     # 国家核安全局爬虫
│   ├── scinet_spider.py  # 科学网爬虫
│   ├── ccnta_spider.py   # 中国核技术网爬虫
│   └── wechat_spider.py  # 微信公众号爬虫
├── utils/           # 工具类
│   ├── __init__.py
│   ├── encoding_detector.py  # 编码检测
│   ├── parse_date.py         # 日期解析
│   ├── storage_handler.py    # 存储处理
│   ├── article_fetch.py      # 文章原文抓取
│   └── qwen_analyzer.py      # Qwen大模型分析
├── output/          # 输出目录
├── __init__.py
├── crawler.py       # 爬虫调度器
├── main.py          # 主入口
├── test.py          # 测试文件
└── we_chat_official_account.json  # 微信公众号列表
```

## 微信公众号 API

微信公众号爬虫使用以下 API：

- **接口地址**：`https://down.mptext.top/api/public/v1/article`
- **请求方式**：GET
- **参数**：
  - `fakeid`：公众号 ID
  - `begin`：起始索引，从 0 开始
  - `size`：返回消息条数，最大不超过 20
- **请求头**：
  - `Cookie: auth-key=你的密钥`

## 输出格式

抓取的文章会保存为 CSV 文件，包含以下字段：

- `title`：文章标题
- `url`：文章链接
- `date`：发布日期
- `source`：文章来源
- `summary`：文章摘要
- `cover`：封面图片链接
- `aid`：文章 ID（仅微信公众号）
- `appmsgid`：公众号文章 ID（仅微信公众号）

## 如何添加新的网站

### 添加新的政策网站或技术网站

1. **创建新的爬虫类**：在 `spiders` 目录下创建一个新的爬虫文件，如 `new_site_spider.py`
2. **继承 BaseSpider**：继承 `BaseSpider` 类并实现 `parse_articles` 和 `get_next_page` 方法
3. **注册爬虫**：在 `main.py` 文件的 `register_policy_spiders` 或 `register_technical_spiders` 函数中添加新的爬虫配置

### 添加新的微信公众号

1. **编辑微信公众号列表**：打开 `wechat_official_account.json` 文件
2. **添加新的公众号**：在 `accounts` 数组中添加新的公众号信息，包含 `fakeid` 和 `nickname` 字段

```json
{
  "version": "1.0",
  "accounts": [
    {
      "fakeid": "MzA3MzcyMjcwNQ==",
      "nickname": "能源日参"
    },
    {
      "fakeid": "新的公众号ID",
      "nickname": "新的公众号名称"
    }
  ]
}
```

## Qwen大模型分析功能

### 功能介绍

该功能使用阿里云的Qwen大模型对抓取的文章进行智能分析，评估其价值并剔除用处不大的内容。分析基于以下五个维度：

1. **信息价值**：内容是否包含有价值的信息
2. **时效性**：信息是否及时、新鲜
3. **深度**：内容是否有深度分析或独特见解
4. **相关性**：内容与能源行业是否相关
5. **实用性**：内容是否具有实用价值

### 评分标准

- **9-10分**：内容非常有价值，包含重要信息、深度分析或独特见解
- **7-8分**：内容有较高价值，包含有用信息或合理分析
- **5-6分**：内容有一定价值，包含一些有用信息
- **3-4分**：内容价值有限，信息较为普通或重复
- **1-2分**：内容价值很低，信息无关或无意义

### 使用方法

1. **获取API密钥**：需要在阿里云DashScope平台注册并获取API密钥
2. **运行爬虫并分析**：使用 `--analyze` 参数启用分析功能

```bash
# 抓取政策新闻并分析
python main.py zc --analyze --api_key YOUR_API_KEY

# 自定义筛选阈值
python main.py js --analyze --api_key YOUR_API_KEY --threshold 6
```

### 分析结果

分析完成后，系统会生成两个文件：
- `analyzed_articles_时间戳.csv`：保留的高价值文章
- `analyzed_articles_时间戳_removed.csv`：移除的低价值文章

每个文件都包含文章的标题、URL、日期、来源、摘要、评分、分析理由和价值等级。

## 注意事项

1. 请遵守网站的 robots.txt 规则
2. 不要过快请求，避免给服务器造成压力
3. 微信公众号 API 需要有效的 auth-key
4. 部分网站可能会有反爬机制，如遇到问题请调整请求频率
5. Qwen大模型分析功能需要有效的阿里云DashScope API密钥
6. 分析过程可能需要较长时间，取决于文章数量和API响应速度

## 许可证

MIT
