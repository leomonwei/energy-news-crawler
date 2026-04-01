# spiders/gkzhan_spider.py
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_spider import BaseSpider

class GkzhanSpider(BaseSpider):
    """智能制造网"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        news_list = soup.find('div', class_='news-list')
        if not news_list:
            return articles

        for li in news_list.find_all('li'):
            # 提取标题和链接
            title_tag = li.find('div', class_='item-left').find('a')
            title = title_tag.get('title', '').strip()
            article_url = urljoin(self.base_url, title_tag['href'])

            # 提取日期
            date_tag = li.find('span', class_='label')
            publish_date = date_tag.text.split(' ')[0] if date_tag else ''


            articles.append({
                'title': title,
                'url': article_url,
                'date': publish_date,
                'source': '智能制造网'
            })
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        next_btn = soup.find('a', class_='lt')
        return urljoin(self.base_url, next_btn['href']) if next_btn else None
