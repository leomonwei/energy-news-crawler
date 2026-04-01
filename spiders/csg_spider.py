# spiders/csg_spider.py
from .base_spider import BaseSpider
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CsgSpider(BaseSpider):
    """南方电网能源观察"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 定位文章列表区域
        list_div = soup.find('div', class_='list-news')
        if not list_div:
            return articles

        # 提取每个文章条目
        for li in list_div.find_all('li'):
            # 提取日期
            date_tag = li.find('span')
            publish_date = date_tag.text.strip() if date_tag else '未知日期'

            # 提取标题和链接
            title_tag = li.find('a')
            if not title_tag:
                continue

            # 处理相对链接
            article_url = urljoin(self.base_url, title_tag['href'])
            
            articles.append({
                'title': title_tag.text.strip(),
                'url': article_url,
                'date': publish_date,
                'source': '南方电网能源观察'
            })
        
        return articles

    def get_next_page(self, html):
        """智能分页解析"""
        soup = BeautifulSoup(html, 'html.parser')
        page_div = soup.find('div', id='page')
        
        # 方法1：直接查找下一页按钮
        if page_div:
            next_btn = page_div.find('a', string='>')
            if next_btn and next_btn.get('href'):
                # 处理禁用状态（当class包含now且没有href时）
                if 'href' in next_btn.attrs:
                    return urljoin(self.base_url, next_btn['href'])
