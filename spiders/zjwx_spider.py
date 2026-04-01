from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_spider import BaseSpider

class ZJwxSpider(BaseSpider):
    """浙江网信网爬虫"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 定位数据存储区域
        data_div = soup.find('div', id='5057777')
        if not data_div:
            return articles
        
        # 提取CDATA数据
        cdata = data_div.find('script', type='text/xml')
        if not cdata:
            return articles

        # 解析嵌套的XML结构
        data_soup = BeautifulSoup(cdata.string, 'xml')
        records = data_soup.find_all('record')
        
        for record in records:
            record_html = BeautifulSoup(record.get_text(), 'html.parser')
            li = record_html.find('li')
            if not li:
                continue

            # 提取文章信息
            link_tag = li.find('a')
            date_tag = li.find('p', class_='r w120 f14_b')
            
            if link_tag and date_tag:
                article_url = urljoin(self.base_url, link_tag['href'])
                articles.append({
                    'title': link_tag.get_text(strip=True),
                    'url': article_url,
                    'date': date_tag.get_text(strip=True),
                    'source': '浙江网信网'
                })
        
        return articles

    def get_next_page(self, html):
        """解析方法"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 寻找带分页标志的下页按钮
        next_btn = soup.find('a', class_='default_pgNext', title='下页')
        
        # 验证有效性
        if next_btn and next_btn.has_attr('href'):
            # 处理URL编码问题（&amp; -> &）
            raw_url = next_btn['href'].replace('&amp;', '&')
            return urljoin(self.base_url, raw_url)
        
        return None
