# spiders/cec_spider.py
import json
import requests
from urllib.parse import urljoin
from datetime import datetime
from .base_spider import BaseSpider

class CECSpider(BaseSpider):
    """中国电力企业联合会媒体聚焦"""
    def __init__(self, base_url, channel_id=707):
        super().__init__(base_url)
        self.channel_id = channel_id  # 栏目ID
        self.base_url = urljoin(base_url, "/ms-mcms/mcms/content/list?id=707&pageNumber=1&pageSize=10")
        # print(f"API URL: {self.base_url}") 
        self.page_size = 10  # 每页数量

    def parse_articles(self, html):
        """解析API返回的JSON数据"""
        try:
            data = json.loads(html)
            if not data.get('success'):
                return []

            articles = []
            for item in data['data'].get('list', []):
                # 转换时间戳（假设是毫秒级）
                pub_date = datetime.fromtimestamp(item['publicTime']/1000).strftime('%Y-%m-%d')
                
                articles.append({
                    'title': item['basicTitle'],
                    'url': 'https://www.cec.org.cn/detail/index.html?3-' + str(item['articleID']),
                    'date': pub_date,
                    'source': '中国电力企业联合会',
                })
            return articles
        except Exception as e:
            print(f"解析数据失败: {e}")
            return []

    def get_next_page(self, html):
        """获取下一页参数"""
        try:
            data = json.loads(html)
            current_page = data['data']['pageNum']
            # print(f"当前页: {current_page}")
            total_page = data['data']['totalPage']
            
            if current_page < total_page:
                # 构建下一页的URL
                next_page_url = self.base_url.replace(f"pageNumber={current_page}", f"pageNumber={current_page + 1}")
                self.base_url = next_page_url
                # print(f"下一页URL: {next_page_url}")
                return next_page_url
            return None
        except:
            return None

    def fetch_page(self, url=None, data=None):
        """重写获取方法以支持分页"""
        target_url = url or self.base_url
        
        try:
            response = requests.get(
                target_url,
                headers=self.headers,
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
            
        except Exception as e:
            print(f"请求失败: {e}")
            return None