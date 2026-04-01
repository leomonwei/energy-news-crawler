# spiders/ccnta_spider.py
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_spider import BaseSpider

class CcntaSpider(BaseSpider):
    """中国核技术网爬虫"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 定位文章列表容器
        list_container = soup.find('div', class_='list')
        if not list_container:
            return articles
        
        # 提取文章条目
        for article_div in list_container.select('div.art > div.li'):
            try:
                # 标题和链接
                title_tag = article_div.find('h2').find('a')
                title = title_tag.get('title', '').strip()
                article_url = urljoin(self.base_url, title_tag['href'])
                
                # 日期和分类
                key_span = article_div.find('span', class_='key')
                date = key_span.find('em').text.strip() if key_span and key_span.find('em') else '未知日期'
                
                articles.append({
                    'title': title,
                    'url': article_url,
                    'date': date,
                    'source': '中国核技术网'
                })
            except Exception as e:
                print(f"解析文章异常: {str(e)}")
                continue
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        pagination = soup.find('div', class_='pagecode')
        if not pagination:
            return None
        
        next_page = pagination.find('a', string='下一页')
        if not next_page or 'disable' in next_page.get('class', []):
            return None
        
        return urljoin(self.base_url, next_page['href'])
