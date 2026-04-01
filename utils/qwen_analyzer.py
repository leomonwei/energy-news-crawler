#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qwen大模型新闻分析工具

该工具基于Qwen大模型对爬取的新闻和公众号文章进行分析，
评估其价值并剔除用处不大的内容。

使用方法:
python qwen_analyzer.py --input articles.csv --output analyzed_articles.csv --api_key YOUR_API_KEY [--batch_size 5] [--threshold 5]
"""

import argparse
import csv
import json
import re
import time
import requests
from tqdm import tqdm
from .article_fetch import scrapling_fetch

class QwenAI:
    """Qwen大模型API封装类"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def invoke(self, payload):
        """调用Qwen API"""
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                return {"error": f"API调用失败，状态码: {response.status_code}"}
        except Exception as e:
            print(f"API调用异常: {e}")
            return {"error": f"API调用异常: {str(e)}"}

class NewsAnalyzer:
    """新闻分析类"""
    
    def __init__(self, api_key, batch_size=5, threshold=5):
        self.api = QwenAI(api_key)
        self.batch_size = batch_size
        self.threshold = threshold
        # 规则过滤配置
        self.filter_rules = {
            # 标题关键词过滤
            'title_keywords': [
                '招聘', '求职', '广告', '推广', '活动', '会议', '通知', '公告',
                '报名', '注册', '抽奖', '福利', '优惠', '促销', '打折'
            ],
            # 来源过滤
            'source_blacklist': [],
            # 标题长度过滤
            'min_title_length': 5,
            'max_title_length': 100
        }
        self.system_prompt = """你是一位专业的新闻分析师，负责评估新闻和公众号文章的价值。请基于以下标准对提供的文章进行分析，评估其价值并提供评分和理由。

评分标准（1-10分）：
- 9-10分：内容非常有价值，包含重要信息、深度分析或独特见解
- 7-8分：内容有较高价值，包含有用信息或合理分析
- 5-6分：内容有一定价值，包含一些有用信息
- 3-4分：内容价值有限，信息较为普通或重复
- 1-2分：内容价值很低，信息无关或无意义

分析维度：
1. 信息价值：内容是否包含有价值的信息
2. 时效性：信息是否及时、新鲜
3. 深度：内容是否有深度分析或独特见解
4. 相关性：内容与能源行业是否相关
5. 实用性：内容是否具有实用价值

你的分析必须严格按照以下JSON格式输出：
{
  "score": 数字(1-10),
  "reason": "详细解释评分理由，基于上述五个维度",
  "value": "高/中/低"  // 根据评分，高(7-10)、中(5-6)、低(1-4)
}"""
    
    def filter_by_rules(self, article):
        """基于规则过滤文章"""
        title = article.get('title', '')
        source = article.get('source', '')
        
        # 检查标题长度
        if len(title) < self.filter_rules['min_title_length'] or len(title) > self.filter_rules['max_title_length']:
            return False, "标题长度不符合要求"
        
        # 检查标题关键词
        for keyword in self.filter_rules['title_keywords']:
            if keyword in title:
                return False, f"标题包含过滤关键词: {keyword}"
        
        # 检查来源黑名单
        if source in self.filter_rules['source_blacklist']:
            return False, f"来源在黑名单中: {source}"
        
        return True, "通过规则过滤"
    
    def fetch_article_content(self, url):
        """抓取文章原文"""
        try:
            content, selector = scrapling_fetch(url)
            return content
        except Exception as e:
            print(f"抓取原文失败: {e}")
            return ""
    
    def analyze_single_article(self, title, source, date, url, summary=""):
        """分析单篇文章"""
        # 抓取原文内容
        content = self.fetch_article_content(url)
        
        user_prompt = f"""请分析以下文章的价值：

标题：{title}
来源：{source}
日期：{date}
URL：{url}
摘要：{summary}

原文内容：
{content[:2000]}  # 限制原文长度，避免超过API限制

请根据信息价值、时效性、深度、相关性和实用性五个维度，评估这篇文章的价值，并给出1-10分的评分、详细理由和价值等级（高/中/低）。严格按照JSON格式输出。"""
        
        payload = {
            "model": "qwen-plus",  # 或其他适合的Qwen模型
            "input": {
                "prompt": user_prompt
            },
            "parameters": {
                "temperature": 0.3,
                "top_p": 0.8,
                "max_new_tokens": 1000
            }
        }
        
        response = self.api.invoke(payload)
        return self.parse_response(response)
    
    def analyze_batch_articles(self, articles_list):
        """批量分析文章"""
        results = []
        
        # 先进行规则过滤
        filtered_articles = []
        for article in articles_list:
            passed, reason = self.filter_by_rules(article)
            if passed:
                filtered_articles.append(article)
            else:
                # 对于未通过规则过滤的文章，直接标记为低价值
                result_with_article = {
                    **article,
                    "score": 1,
                    "reason": f"未通过规则过滤: {reason}",
                    "value": "低"
                }
                results.append(result_with_article)
        
        # 对通过规则过滤的文章进行批量分析
        for i in range(0, len(filtered_articles), self.batch_size):
            batch = filtered_articles[i:i+self.batch_size]
            
            # 构建批量处理的提示词
            user_prompt = "请分析以下多篇文章的价值，并逐条给出评估结果：\n\n"
            
            for idx, article in enumerate(batch, 1):
                # 抓取原文内容
                content = self.fetch_article_content(article['url'])
                user_prompt += f"""文章{idx}：
标题：{article['title']}
来源：{article['source']}
日期：{article['date']}
URL：{article['url']}
摘要：{article.get('summary', '')}

原文内容：
{content[:1000]}  # 限制原文长度，避免超过API限制

"""
            
            user_prompt += """请根据信息价值、时效性、深度、相关性和实用性五个维度，逐条评估这些文章的价值，并给出1-10分的评分、详细理由和价值等级（高/中/低）。每条文章的分析必须严格按照以下JSON格式输出，并用"---"分隔不同文章的分析结果：

{
  "article_index": 1,
  "score": 数字(1-10),
  "reason": "详细解释评分理由",
  "value": "高/中/低"
}
---
{
  "article_index": 2,
  ...
}"""
            
            payload = {
                "model": "qwen-plus",
                "input": {
                    "prompt": user_prompt
                },
                "parameters": {
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "max_new_tokens": 4000
                }
            }
            
            response = self.api.invoke(payload)
            batch_results = self.parse_batch_response(response, len(batch))
            
            # 将批次结果与原始文章数据合并
            for j, result in enumerate(batch_results):
                if j < len(batch):  # 防止索引越界
                    result_with_article = {**batch[j], **result}
                    results.append(result_with_article)
            
            # API调用间隔，避免频率限制
            if i + self.batch_size < len(filtered_articles):
                time.sleep(1)
        
        return results
    
    def parse_response(self, response):
        """解析单篇文章的API响应"""
        try:
            # 检查是否有错误
            if "error" in response:
                return {
                    "score": 0,
                    "reason": f"API调用错误: {response.get('error')}",
                    "value": "低"
                }
            
            # 获取模型输出内容
            content = response.get("output", {}).get("text", "")
            
            # 尝试直接解析整个内容
            try:
                result = json.loads(content)
                return {
                    "score": int(result.get("score", 0)),
                    "reason": result.get("reason", ""),
                    "value": result.get("value", "低")
                }
            except:
                # 如果直接解析失败，尝试使用正则表达式提取JSON部分
                json_pattern = r'\{[\s\S]*\}'
                match = re.search(json_pattern, content)
                if match:
                    json_str = match.group(0)
                    result = json.loads(json_str)
                    return {
                        "score": int(result.get("score", 0)),
                        "reason": result.get("reason", ""),
                        "value": result.get("value", "低")
                    }
            
            # 如果仍然失败，返回默认值
            return {
                "score": 0,
                "reason": "无法解析API响应",
                "value": "低"
            }
        except Exception as e:
            print(f"解析API响应时出错: {e}")
            return {
                "score": 0,
                "reason": f"解析错误: {str(e)}",
                "value": "低"
            }
    
    def parse_batch_response(self, response, batch_size):
        """解析批量文章的API响应"""
        try:
            # 检查是否有错误
            if "error" in response:
                return [{"article_index": i+1, "score": 0, "reason": f"API调用错误: {response.get('error')}", "value": "低"} 
                        for i in range(batch_size)]
            
            # 获取模型输出内容
            content = response.get("output", {}).get("text", "")
            
            # 使用分隔符分割不同文章的分析结果
            results_str = content.split("---")
            
            results = []
            for result_str in results_str:
                if not result_str.strip():
                    continue
                    
                try:
                    # 尝试提取并解析JSON
                    json_pattern = r'\{[\s\S]*?\}'
                    match = re.search(json_pattern, result_str)
                    if match:
                        json_str = match.group(0)
                        result = json.loads(json_str)
                        
                        # 提取article_index确保顺序正确
                        article_index = result.get("article_index", 0)
                        
                        results.append({
                            "article_index": article_index,
                            "score": int(result.get("score", 0)),
                            "reason": result.get("reason", ""),
                            "value": result.get("value", "低")
                        })
                except Exception as e:
                    # 如果解析失败，添加一个默认结果
                    results.append({
                        "article_index": len(results) + 1,
                        "score": 0,
                        "reason": f"无法解析该篇文章的分析结果: {str(e)}",
                        "value": "低"
                    })
            
            # 确保结果数量与预期一致
            while len(results) < batch_size:
                results.append({
                    "article_index": len(results) + 1,
                    "score": 0,
                    "reason": "API响应中缺少该篇文章的分析结果",
                    "value": "低"
                })
                
            # 按article_index排序
            results.sort(key=lambda x: x["article_index"])
            
            # 移除article_index字段，因为它只是用于排序
            for result in results:
                if "article_index" in result:
                    del result["article_index"]
            
            return results
        except Exception as e:
            print(f"解析批量API响应时出错: {e}")
            # 返回默认结果
            return [{"score": 0, "reason": f"批量解析错误: {str(e)}", "value": "低"} 
                    for i in range(batch_size)]

    def filter_articles(self, analyzed_articles):
        """根据评分过滤文章"""
        filtered = []
        removed = []
        
        for article in analyzed_articles:
            score = article.get("score", 0)
            if score >= self.threshold:
                filtered.append(article)
            else:
                removed.append(article)
        
        return filtered, removed

def read_articles_csv(file_path):
    """读取文章CSV文件"""
    articles_list = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                articles_list.append({
                    'title': row.get('title', ''),
                    'url': row.get('url', ''),
                    'date': row.get('date', ''),
                    'source': row.get('source', ''),
                    'summary': row.get('summary', ''),
                    'cover': row.get('cover', ''),
                    'aid': row.get('aid', ''),
                    'appmsgid': row.get('appmsgid', '')
                })

        return articles_list
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return []

def write_analyzed_articles_csv(file_path, articles_list):
    """将分析结果写入CSV文件"""
    try:
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['title', 'url', 'date', 'source', 'summary', 'cover', 'aid', 'appmsgid', 'score', 'reason', 'value']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for article in articles_list:
                writer.writerow({
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'date': article.get('date', ''),
                    'source': article.get('source', ''),
                    'summary': article.get('summary', ''),
                    'cover': article.get('cover', ''),
                    'aid': article.get('aid', ''),
                    'appmsgid': article.get('appmsgid', ''),
                    'score': article.get('score', 0),
                    'reason': article.get('reason', ''),
                    'value': article.get('value', '低')
                })
        print(f"分析结果已保存到 {file_path}")
        return True
    except Exception as e:
        print(f"写入CSV文件时出错: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Qwen大模型新闻分析工具')
    parser.add_argument('--input', required=True, help='输入CSV文件路径')
    parser.add_argument('--output', required=True, help='输出CSV文件路径')
    parser.add_argument('--api_key', required=True, help='阿里云DashScope API密钥')
    parser.add_argument('--batch_size', type=int, default=5, help='批处理大小')
    parser.add_argument('--threshold', type=int, default=5, help='筛选阈值，高于此分数的文章会被保留')
    
    args = parser.parse_args()
    
    # 读取文章数据
    print(f"正在读取文章数据: {args.input}")
    articles_list = read_articles_csv(args.input)
    if not articles_list:
        print("未读取到有效的文章数据，程序退出")
        return
    
    print(f"共读取 {len(articles_list)} 篇文章")
    
    # 初始化文章分析器
    analyzer = NewsAnalyzer(args.api_key, args.batch_size, args.threshold)
    
    # 批量分析文章
    print("正在分析文章价值...")
    analyzed_articles = analyzer.analyze_batch_articles(articles_list)
    
    # 过滤文章
    filtered_articles, removed_articles = analyzer.filter_articles(analyzed_articles)
    
    print(f"\n分析完成:")
    print(f"总文章数: {len(analyzed_articles)}")
    print(f"保留文章数: {len(filtered_articles)}")
    print(f"移除文章数: {len(removed_articles)}")
    
    # 写入分析结果
    write_analyzed_articles_csv(args.output, filtered_articles)
    
    # 如果有移除的文章，也保存下来
    if removed_articles:
        removed_output = args.output.replace('.csv', '_removed.csv')
        write_analyzed_articles_csv(removed_output, removed_articles)
        print(f"移除的文章已保存到 {removed_output}")

if __name__ == "__main__":
    main()
