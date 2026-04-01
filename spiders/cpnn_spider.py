# spiders/cpnn_spider.py
from .base_spider import BaseSpider
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CpnnSpider(BaseSpider):
    """中国能源新闻网"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        list_div = soup.find('div', class_='cpnnlist_l')
        if not list_div:
            return articles

        for li in list_div.find_all('li'):
            link = li.find('a')
            if not link:
                continue

            article_url = urljoin(self.base_url, link['href'])
            date_tag = li.find('b', class_='fr')
            
            articles.append({
                'title': link.get('title', '').strip(),
                'url': article_url,
                'date': date_tag.text.strip() if date_tag else '未知日期',
                'source': '中国能源新闻网'
            })
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        next_page = soup.select_one('a#pagenav_1[href^="index_"]')
        return urljoin(self.base_url, next_page['href']) if next_page else None