# spiders/science_net_spider.py（修正版）
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_spider import BaseSpider

class ScienceNetSpider(BaseSpider):
    """科学网信息科学新闻爬虫（修复版）"""
    def __init__(self, base_url):
        super().__init__(base_url)
        self.session = requests.Session()  # 使用Session保持状态
        self.viewstate = None
        self.event_validation = None

    def fetch_page(self, url=None, data=None):
        """增强请求方法"""
        target_url = url or self.base_url
        try:
            if data:
                response = self.session.post(
                    target_url,
                    headers=self.headers,
                    data=data,
                    timeout=10
                )
            else:
                response = self.session.get(
                    target_url,
                    headers=self.headers,
                    timeout=10
                )
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"请求失败: {str(e)}")
            return None

    def parse_articles(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 安全提取隐藏字段
            viewstate_tag = soup.find('input', {'name': '__VIEWSTATE'})
            event_validation_tag = soup.find('input', {'name': '__EVENTVALIDATION'})
            
            self.viewstate = viewstate_tag['value'] if viewstate_tag else ''
            self.event_validation = event_validation_tag['value'] if event_validation_tag else ''

            articles = []
            data_grid = soup.find('table', id='DataGrid1')
            
            if data_grid:
                for row in data_grid.find_all('tr'):
                    if row.find('td', height="20"):
                        continue
                    
                    # 安全提取链接
                    link_tag = row.find('a')
                    if not link_tag:
                        continue
                    
                    # 构建文章信息
                    article_url = urljoin(self.base_url, link_tag.get('href', ''))
                    tds = row.find_all('td')
                    
                    if len(tds) >= 3:
                        articles.append({
                            'title': link_tag.get_text().strip(),
                            'url': article_url,
                            'date': tds[2].get_text().strip(),
                            'source': '科学网'
                        })
                        
            return articles
            
        except Exception as e:
            print(f"解析失败: {str(e)}")
            return []

    def get_next_page(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            next_btn = soup.find('a', class_='highlight2', string='>')
            
            if next_btn and 'href' in next_btn.attrs:
                match = re.search(r"__doPostBack\('.*?','(\d+)'\)", next_btn['href'])
                if match:
                    return {
                        'url': self.base_url,
                        'method': 'POST',
                        'data': {
                            '__VIEWSTATE': self.viewstate,
                            '__EVENTVALIDATION': self.event_validation,
                            '__EVENTTARGET': 'AspNetPager1',
                            '__EVENTARGUMENT': match.group(1)
                        }
                    }
            return None
        except Exception as e:
            print(f"分页解析失败: {str(e)}")
            return None
