# spiders/escn_spider.py
from .base_spider import BaseSpider
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class ESCNSpider(BaseSpider):
    """中国储能网爬虫"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        list_ul = soup.find('ul', class_='n-onelist')
        if not list_ul:
            return articles

        for li in list_ul.find_all('li'):
            link = li.find('a')
            if not link:
                continue

            # 处理相对链接
            article_url = urljoin(self.base_url, link['href'])
            
            # 提取发布日期
            date_span = li.find('span')
            publish_date = date_span.text.strip() if date_span else '未知日期'
            
            articles.append({
                'title': link.text.strip(),
                'url': article_url,
                'date': publish_date,
                'source': '中国储能网'
            })
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        next_page = soup.select_one('.page-box .digg a:not([href*="javascript"])')
        return urljoin(self.base_url, next_page['href']) if next_page else None
