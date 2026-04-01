# spider/hydroe_spider.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from spiders.base_spider import BaseSpider  # 使用之前设计的基类

class HydrogenEnergySpider(BaseSpider):
    """全球氢能网"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 定位文章表格（每个table包含一篇文章）
        article_tables = soup.select('table.f16[width="880"]')
        
        for table in article_tables:
            try:
                # 提取标题和链接
                title_tag = table.select_one('h2 a')
                if not title_tag:
                    continue
                
                article_url = urljoin(self.base_url, title_tag['href'])
                title = title_tag.get('title', '').strip() or title_tag.text.strip()
                
                # 提取日期
                date_tag = table.select_one('td.fgray2')
                publish_date = date_tag.text.strip() if date_tag else '未知日期'
                
                
                articles.append({
                    'title': title,
                    'url': article_url,
                    'date': publish_date,
                    'source': '全球氢能网'
                })
            except Exception as e:
                print(f"解析文章时出错: {str(e)}")
                continue
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        next_page_tag = soup.find('a', string='下一页')
        
        if next_page_tag and 'href' in next_page_tag.attrs:
            return urljoin(self.base_url, next_page_tag['href'])
        return None