# 在spiders目录下新建cinn_spider.py
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_spider import BaseSpider

class CinnSpider(BaseSpider):
    """中国工业新闻网"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 定位文章列表容器
        list_container = soup.find('div', class_='list-news-box')
        if not list_container:
            return articles

        # 遍历每个文章条目
        for item in list_container.find_all('div', class_='item-box'):
            try:
                # 提取标题和链接
                title_tag = item.find('div', class_='tit').find('a')
                title = title_tag.text.strip()
                relative_url = title_tag['href']
                article_url = urljoin(self.base_url, relative_url)

                # 提取发布时间
                date_tag = item.find('div', class_='info').find('span', string=lambda t: re.match(r'\d{4}-\d{2}-\d{2}', t))
                # print(date_tag)

                articles.append({
                    'title': title,
                    'url': article_url,
                    'date': date_tag.text.strip() if date_tag else '未知时间',
                    'source': '中国工业新闻网'
                })
            except Exception as e:
                print(f"解析文章异常: {str(e)}")
                continue
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        pagination = soup.find('div', class_='page ov')

        if not pagination:
            return None

        # 查找有效的下一页按钮（包含next类且不包含disable类）
        next_page = pagination.find('a', class_='next', attrs={'href': True})
        
        if not next_page or 'disable' in next_page.get('class', []):
            return None

        # 处理相对路径
        return urljoin(self.base_url, next_page['href'])
