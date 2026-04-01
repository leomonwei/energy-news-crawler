# spiders/nengyuanjie_spider.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_spider import BaseSpider

class NyjieSpider(BaseSpider):
    """能源界网站"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        list_div = soup.find('div', class_='lists')
        if not list_div:
            return articles

        for item in list_div.find_all('div', class_='li'):
            link = item.find('a', href=True)
            if not link:
                continue

            # 处理相对链接
            article_url = urljoin(self.base_url, link['href'])
            
            # 提取标题
            title = link.get('title', '').strip()

            # 提取日期
            date_tag = item.find('span', class_='txt')
            publish_date = date_tag.get_text(strip=True) if date_tag else ''

            articles.append({
                'title': title,
                'url': article_url,
                'date': publish_date,
                'source': '能源界'
            })
        
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
