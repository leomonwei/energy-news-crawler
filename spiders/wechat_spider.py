# spiders/wechat_spider.py
import json
import requests
from spiders.base_spider import BaseSpider
from datetime import datetime
import time

class WeChatSpider(BaseSpider):
    """微信公众号爬虫"""
    def __init__(self, base_url, fakeid, auth_key, nickname):
        super().__init__(base_url)
        self.fakeid = fakeid
        self.auth_key = auth_key
        self.nickname = nickname
        # 添加Cookie到请求头
        self.headers['Cookie'] = f'auth-key={auth_key}'
        self.headers['Accept'] = 'application/json, text/plain, */*'
        self.begin = 0
        self.size = 20  # 最大返回条数
    
    def fetch_page(self, url=None, data=None):
        """获取API数据"""
        time.sleep(2)  # 避免过快请求
        target_url = url or self.base_url
        try:
            # 构建请求参数
            params = {
                'fakeid': self.fakeid,
                'begin': self.begin,
                'size': self.size
            }
            
            resp = self.session.get(
                target_url, 
                headers=self.headers, 
                params=params, 
                timeout=(5, 15)
            )
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.ConnectTimeout:
            print(f"请求连接超时: {target_url}")
            return None
        except requests.exceptions.ReadTimeout:
            print(f"请求响应超时: {target_url}")
            return None
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def parse_articles(self, html):
        """解析文章列表"""
        articles = []
        if not html:
            return articles
        
        try:
            # 尝试解析JSON
            import json
            data = json.loads(html)
            
            # 检查API响应
            base_resp = data.get('base_resp', {})
            if base_resp.get('ret') != 0:
                print(f"API返回错误: {base_resp.get('err_msg', '未知错误')}")
                return articles
            
            # 解析文章数据
            for item in data.get('articles', []):
                article = {
                'title': item.get('title', ''),
                'url': item.get('link', '').strip(),
                'date': self._format_date(item.get('update_time')),
                'source': self.nickname,
                'summary': item.get('digest', ''),
                'cover': item.get('cover', '').strip(),
                'aid': item.get('aid', ''),
                'appmsgid': item.get('appmsgid', '')
            }
                articles.append(article)
            
            return articles
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"响应内容: {html[:500]}...")
            return articles
    
    def get_next_page(self, html):
        """获取下一页"""
        if not html:
            return None
        
        try:
            import json
            data = json.loads(html)
            
            # 检查是否有更多数据
            articles = data.get('articles', [])
            if len(articles) < self.size:
                return None
            
            # 增加起始索引
            self.begin += self.size
            return self.base_url
        except json.JSONDecodeError:
            return None
    
    def _format_date(self, timestamp):
        """格式化时间戳为日期字符串"""
        if not timestamp:
            return ''
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return ''