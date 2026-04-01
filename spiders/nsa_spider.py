# spiders/nsa_spider.py
from .base_spider import BaseSpider
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class NsaSpider(BaseSpider):
    """核安全热点每月一题爬虫"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 处理每个主题区块
        for section in soup.find_all('div', class_='myyt_body'):
            # 提取月份信息
            title_tag = section.find('div', class_='title')
            if not title_tag:
                continue
            
            # 正则提取日期 "XXXX年XX月" 格式
            date_match = re.search(r'(\d{4})年(\d{1,2})月', title_tag.text)
            if not date_match:
                continue
            
            year, month = date_match.groups()
            publish_date = f"{year}-{month.zfill(2)}-01"  # 默认当月第一天

            # 提取文章条目
            for li in section.find_all('li'):
                link = li.find('a', class_='cjcx_biaobnan')
                if not link:
                    continue

                # 构建完整URL
                absolute_url = urljoin(self.base_url, link['href'])
                
                articles.append({
                    'title': link.text.strip(),
                    'url': absolute_url,
                    'date': publish_date,
                    'source': '核安全热点每月一题'
                })
        
        return articles

    def get_next_page(self, html):
        # 该网站采用动态加载分页，暂不处理分页
        return None