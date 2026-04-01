# spiders/bjx_spider.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_spider import BaseSpider

class BjxBaseSpider(BaseSpider):
    """北极星网站基类"""
    def parse_articles(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 抽象方法由子类实现
        list_container = self.get_list_container(soup)
        # print(f"list_container: {list_container}")
        if not list_container:
            return articles

        for li in list_container.find_all('li') or list_container.find_all('div', class_='item'):
            # print(li)
            link = self.get_article_link(li)
            if not link:
                continue
            
            article_url = urljoin(self.base_url, link['href'])
            # print(f"article_url: {article_url}")
            date_tag = self.get_date_tag(li)
            # print(f"date_tag: {date_tag}")
            
            articles.append({
                'title': link.get('title', link.text).strip() or link.text.strip(),
                'url': article_url,
                'date': date_tag.text.strip() if date_tag else '未知日期',
                'source': "北极星电力网"
            })
        
        return articles

    def get_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        pagination = self.get_pagination_container(soup)
        if not pagination:
            return None
        
        next_page = pagination.find('a', string='下一页')
        if not next_page or 'disable' in next_page.get('class', []):
            return None
        
        return urljoin(self.base_url, next_page['href'])

    # 抽象方法定义
    def get_list_container(self, soup):
        raise NotImplementedError

    def get_article_link(self, li):
        raise NotImplementedError

    def get_date_tag(self, li):
        raise NotImplementedError

    def get_pagination_container(self, soup):
        raise NotImplementedError

class BjxUsualSpider(BjxBaseSpider):
    """普通栏目"""
    def get_list_container(self, soup):
        return soup.find('div', class_='cc-list-content')

    def get_article_link(self, li):
        return li.find('a')

    def get_date_tag(self, li):
        return li.find('span')

    def get_pagination_container(self, soup):
        return soup.find('div', class_='cc-paging')

class BjxCarbonSpider(BjxBaseSpider):
    """碳管家栏目"""
    def get_list_container(self, soup):
        return soup.find('ul', class_='news-list-ul')

    def get_article_link(self, li):
        return li.find('a')

    def get_date_tag(self, li):
        return li.find('i')

    def get_pagination_container(self, soup):
        return soup.find('div', class_='page')

class BjxIesSpider(BjxBaseSpider):
    """综合能源栏目，使用查看更多后的网页url"""   
    def get_list_container(self, soup):
        return soup.find('div', class_='cc-list')

    def get_article_link(self, li):
        top_div = li.find('div', class_='top')
        return top_div.find('a')

    def get_date_tag(self, li):
        bottom_div = li.find('div', class_='bottom')
        date_tag = bottom_div.find('div', class_ = 'right').find('p')
        return date_tag.find_all('em')[-1]

    def get_pagination_container(self, soup):
        return soup.find('div', class_='cc-paging')

class BjxGridSpider(BjxBaseSpider):
    """智能电网栏目"""   
    def get_list_container(self, soup):
        return soup.find('ul', class_='list_left_ul')

    def get_article_link(self, li):
        return li.find('a')

    def get_date_tag(self, li):
        return li.find('span')

    def get_pagination_container(self, soup):
        return soup.find('div', class_='page')