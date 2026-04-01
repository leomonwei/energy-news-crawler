# spiders/inen_spider.py
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from spiders.base_spider import BaseSpider

class InEnSpider(BaseSpider):
    """国际电力网"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 定位文章列表区域
        list_ul = soup.find('ul', class_='infoList')
        if not list_ul:
            return articles

        # 遍历每个文章条目
        for li in list_ul.find_all('li'):
            try:
                # 提取标题和链接
                title_tag = li.find('h5').find('a')
                title = title_tag.text.strip()
                article_url = urljoin(self.base_url, title_tag['href'])

                # 提取发布日期
                date_tag = li.find('i')
                publish_date = date_tag.text.strip() if date_tag else '未知日期'

                articles.append({
                    'title': title,
                    'url': article_url,
                    'date': publish_date,
                    'source': '国际电力网'
                })
            except Exception as e:
                print(f"解析文章异常: {str(e)}")
                continue
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        next_page = soup.find('a', string=lambda t: t and '下一页' in t)
        return urljoin(self.base_url, next_page['href']) if next_page else None
