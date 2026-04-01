# crawler.py
"""
支持多网站并发的爬虫调度器
版本：2.0
- 增强错误处理和重试机制
- 支持指数退避策略
- 改进编码处理
"""
import concurrent.futures
import time
import random
from typing import List, Dict, Optional
from spiders.base_spider import BaseSpider
from utils.storage_handler import CSVStorage, ExcelStorage
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

class Crawler:
    """支持多网站并发的爬虫调度器 v2.0"""
    
    # 常见 User-Agent 列表（反爬）
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, max_workers: int = 3, timeout: int = 30, retry: int = 3):
        """
        初始化爬虫调度器
        
        Args:
            max_workers: 最大并发线程数
            timeout: 请求超时时间（秒）
            retry: 重试次数
        """
        self.spiders: Dict[str, BaseSpider] = {}
        self.max_workers = max_workers
        self.timeout = timeout
        self.retry = retry
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def add_spider(self, name: str, spider: BaseSpider):
        """注册爬虫"""
        self.spiders[name] = spider

    def _get_random_user_agent(self) -> str:
        """获取随机 User-Agent"""
        return random.choice(self.USER_AGENTS)

    def _fetch_with_retry(self, url: str, data: Optional[dict] = None) -> Optional[str]:
        """
        带重试的页面抓取
        
        Args:
            url: 目标 URL
            data: POST 数据（可选）
            
        Returns:
            页面 HTML 内容，失败返回 None
        """
        headers = {'User-Agent': self._get_random_user_agent()}
        
        for attempt in range(self.retry):
            try:
                # 指数退避：1s, 2s, 4s...
                if attempt > 0:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"    重试 {attempt}/{self.retry}，等待 {wait_time:.1f}秒...")
                    time.sleep(wait_time)
                
                # 发送请求
                if data:
                    response = self.session.post(
                        url, 
                        data=data, 
                        headers=headers,
                        timeout=self.timeout,
                        verify=False  # 跳过 SSL 验证（部分网站证书问题）
                    )
                else:
                    response = self.session.get(
                        url, 
                        headers=headers,
                        timeout=self.timeout,
                        verify=False
                    )
                
                # 检查响应状态
                if response.status_code == 200:
                    # 使用与 BaseSpider 相同的编码检测逻辑
                    from utils.encoding_detector import EncodingDetector
                    encoding = EncodingDetector.detect(
                        response.content,
                        response.headers.get('Content-Type')
                    )
                    return response.content.decode(encoding, errors='replace')
                elif response.status_code in [429, 503, 502]:
                    # 限流或服务器错误，重试
                    print(f"    状态码 {response.status_code}，等待重试...")
                    continue
                elif response.status_code == 404:
                    print(f"    页面不存在 (404): {url[:80]}...")
                    return None
                else:
                    print(f"    状态码 {response.status_code}")
                    return None
                    
            except Timeout:
                print(f"    请求超时 ({self.timeout}秒)")
            except ConnectionError as e:
                print(f"    连接错误：{str(e)[:50]}")
            except RequestException as e:
                print(f"    请求异常：{str(e)[:50]}")
            except Exception as e:
                print(f"    未知错误：{str(e)[:50]}")
        
        return None

    def _run_single(self, spider_name: str, max_pages: int, debug: bool = False) -> List[dict]:
        """
        单个爬虫执行逻辑
        
        Args:
            spider_name: 爬虫名称
            max_pages: 最大抓取页数
            debug: 是否启用调试模式
            
        Returns:
            文章列表
        """
        spider = self.spiders.get(spider_name)
        if not spider:
            print(f"  ✗ {spider_name}: 爬虫未找到")
            return []
        
        results = []
        current_url = spider.base_url
        request_data = None
        page_count = 0
        
        if debug:
            print(f"  → {spider_name} 开始抓取：{current_url[:80]}...")
        
        while current_url and page_count < max_pages:
            try:
                # 抓取页面（使用spider的fetch_page方法）
                html = spider.fetch_page(current_url, data=request_data)
                
                if not html:
                    if debug:
                        print(f"  ✗ {spider_name} 第{page_count+1}页：抓取失败")
                    break
                
                # 解析文章
                articles = spider.parse_articles(html)
                results.extend(articles)
                
                if debug:
                    print(f"  ✓ {spider_name} 第{page_count+1}页：{len(articles)}篇")
                
                # 获取下一页
                next_page = spider.get_next_page(html)
                if not next_page:
                    break
                
                # 处理分页请求参数
                if isinstance(next_page, dict):
                    current_url = next_page.get('url', spider.base_url)
                    request_data = next_page.get('data')
                else:
                    current_url = next_page
                    request_data = None
                
                page_count += 1
                
                # 礼貌性延迟（避免过快请求）
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                if debug:
                    print(f"  ✗ {spider_name} 抓取异常：{str(e)[:100]}")
                break
        
        return results

    def run_multi(self, spider_names: List[str], max_pages: int = 3, debug: bool = False) -> Dict[str, List[dict]]:
        """
        并发执行多个爬虫
        
        Args:
            spider_names: 爬虫名称列表
            max_pages: 最大抓取页数
            debug: 是否启用调试模式
            
        Returns:
            各站点文章字典
        """
        futures = {}
        results = {}
        
        # 提交任务到线程池
        for name in spider_names:
            if name in self.spiders:
                future = self.executor.submit(
                    self._run_single, name, max_pages, debug
                )
                futures[future] = name
            else:
                print(f"  ⚠ {name}: 爬虫未注册")
                results[name] = []
        
        # 收集结果
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result(timeout=self.timeout * max_pages * 2)
            except concurrent.futures.TimeoutError:
                print(f"  ✗ {name}: 执行超时")
                results[name] = []
            except Exception as e:
                print(f"  ✗ {name}: {str(e)[:50]}")
                results[name] = []
        
        return results

    def shutdown(self):
        """关闭线程池和会话"""
        self.executor.shutdown(wait=True)
        self.session.close()

    def save_data(self, data: List[Dict], storage_type: str, file_path: str, encoding: str = 'utf-8-sig', **kwargs):
        """
        存储数据
        
        Args:
            data: 数据列表
            storage_type: 存储类型 (csv/excel)
            file_path: 输出文件路径
            encoding: 文件编码（默认 utf-8-sig，兼容 Excel）
            **kwargs: 其他参数
        """
        handlers = {
            'csv': CSVStorage(),
            'excel': ExcelStorage(),
        }
        
        handler = handlers.get(storage_type.lower())
        if not handler:
            raise ValueError(f"不支持的存储类型：{storage_type}")
        
        # 清理数据（移除无效字符）
        cleaned_data = []
        for item in data:
            cleaned_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    # 移除控制字符，保留正常文本
                    cleaned_value = ''.join(
                        char for char in value 
                        if ord(char) >= 32 or char in '\n\r\t'
                    )
                    cleaned_item[key] = cleaned_value.strip()
                else:
                    cleaned_item[key] = value
            cleaned_data.append(cleaned_item)
        
        try:
            # 传递编码参数
            if storage_type.lower() == 'csv':
                handler.save(cleaned_data, file_path=file_path, encoding=encoding)
            else:
                handler.save(cleaned_data, file_path=file_path, **kwargs)
        except Exception as e:
            print(f"存储失败：{e}")
            raise
