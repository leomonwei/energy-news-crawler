# spiders/cnes_spider.py
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_spider import BaseSpider

class CNESSpider(BaseSpider):
    """储能中国网"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 统一使用CSS选择器定位
        article_items = soup.select('div.main2 div.xwt')
        if not article_items:
            print("警告：未检测到文章列表")
            return articles

        for item in article_items:
            try:
                # 检测布局版本
                if item.select_one('div.xwt_left'):
                    # 新版布局：左侧图片+右侧文本
                    title_block = item.select_one('div.xwt_right_a a')
                    date_block = item.select_one('div.xwt_right_c p.p1')
                else:
                    # 旧版布局：纯文本布局
                    title_block = item.select_one('div.xwt_a a')
                    date_block = item.select_one('div.xwt_c p.p1')

                # 通用字段提取
                title = title_block.get('title', title_block.text.strip())
                url = urljoin(self.base_url, title_block['href'])
                date = date_block.text.strip() if date_block else "日期未知"
                
                articles.append({
                    'title': title,
                    'url': url,
                    'date': date,
                    'source': '储能中国网'
                })
            except Exception as e:
                print(f"解析文章时发生异常：{str(e)}")
                continue  # 跳过错误条目继续处理其他内容
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        pages_div = soup.find('div', class_='epages')
        if not pages_div:
            return None
            
        # 查找包含"下一页"的链接
        next_page = pages_div.find('a', string='下一页')
        if next_page and 'href' in next_page.attrs:
            return urljoin(self.base_url, next_page['href'])
        
