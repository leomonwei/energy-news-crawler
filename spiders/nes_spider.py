# spiders/nes_spider.py
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_spider import BaseSpider

class NewEnergySpider(BaseSpider):
    """新能源网"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 精确匹配文章行
        rows = soup.select('tr.member_tr_row')
        
        for row in rows:
            try:
                # 提取标题和链接
                title_cell = row.select_one('td:nth-of-type(2)')
                link_tag = title_cell.find('a')
                if not link_tag:
                    continue
                
                # 处理相对链接
                article_url = urljoin(self.base_url, link_tag['href'])
                
                # 提取发布日期
                date_cell = row.select_one('td:nth-of-type(3)')
                publish_date = date_cell.get_text(strip=True) if date_cell else '未知日期'
                
                # 优化标题提取（优先取title属性）
                title = link_tag.get('title', '').strip() or link_tag.get_text(strip=True)
                
                articles.append({
                    'title': title,
                    'url': article_url,
                    'date': publish_date,
                    'source': '新能源网'
                })
            except Exception as e:
                print(f"解析文章时出错: {str(e)}")
                continue
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        next_page = soup.find('a', text='下一页')
        return urljoin(self.base_url, next_page['href']) if next_page else None
