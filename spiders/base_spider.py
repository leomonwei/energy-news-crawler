# spiders/base_spider.py
import requests
from abc import ABC, abstractmethod
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
import random
from utils.encoding_detector import EncodingDetector
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class BaseSpider(ABC):
    """爬虫抽象基类"""
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
            'Referer': self.base_url,  # 关键：添加Referer，值为网站主域名
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        # 使用 Session 并添加重试策略，避免单次短暂网络抖动导致失败
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], raise_on_status=False)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch_page(self, url=None, data=None):
        """通用页面获取方法"""
        time.sleep(random.uniform(0.5, 1.5))  # 随机等待
        target_url = url or self.base_url
        try:
            # 指定超时（连接 + 响应），避免无限等待
            resp = self.session.get(target_url, headers=self.headers, timeout=(5, 15))
            resp.raise_for_status()

            # 自动检测编码
            encoding = EncodingDetector.detect(
                resp.content,
                resp.headers.get('Content-Type')
            )
            return resp.content.decode(encoding, errors='replace')

        except requests.exceptions.ConnectTimeout:
            print(f"请求连接超时: {target_url}")
            return None
        except requests.exceptions.ReadTimeout:
            print(f"请求响应超时: {target_url}")
            return None
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None

    @abstractmethod
    def parse_articles(self, html):
        """解析文章列表（子类必须实现）"""
        pass

    @abstractmethod
    def get_next_page(self, html):
        """获取下一页链接（子类必须实现）"""
        pass