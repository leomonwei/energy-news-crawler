# spiders/energy_lib_spider.py
import json
import requests
from urllib.parse import urlencode, urljoin
from .base_spider import BaseSpider

class EnergyLibSpider(BaseSpider):
    """能源知识服务平台"""
    def __init__(self, base_url):
        """
        Args:
            base_url: API基础地址 
            page_size: 每页数据量（默认10）
        """
        super().__init__(base_url)
        self.base_url = urljoin(base_url, "/choiceness/getChoiceness?serverId=109&page=1&size=10&sort=recomTime&direction=DESC&orgName=&majorDomainClassify=&classifyName=%E5%8A%A8%E6%80%81%E8%B5%84%E8%AE%AF&classifyId=557&order=&classifyIds=&topicId=&year=&searchType=&searchName=&searchTime=&pushTopics=&searchPeriod=&controlType=&dataType=&serverIds=&selectType=&selectValue=&search=&timePeriod=&directionName=&serverName=&recomTimeStr=&editUserName=&directionId=&domains=&editClassifyIds=&domainId=&domainChildId=&directionNewId=&domainChildName=&startTime=&endTime=&portalFlag=&portalInfoType=&iframeParam=&topicsIframe=&objects_target=&topics_target=&recommendIds=&delIds=&editClassifyNames=")
        
        # 初始化请求头
        self.headers.update({
            'cookie': "sl-session=Ju1wfniEEGhHiTvN94Qz5g==; sl-challenge-server=cloud; STM-SID=81674f2a-6f0f-4f05-bb5b-c2967c09a9f5; JSESSIONID=797115FF40AF754ED6E2B29BBF0ECFB1; sl_jwt_session=J8zPVqzaTDMDpRnJk81PVp3vBQEINyubwB6W9WQWLrRmpFc/2vi1OinSYb7EYKrO; sl_jwt_sign="
        })
    
    def parse_articles(self, html):
        """解析文章列表"""
        try:
            data = json.loads(html)
            if data.get("code") != "200":
                return []
            
            return [
                {
                    "title": item["title"],
                    "url": f"https://energy.whlib.ac.cn/choiceness/getChoicenessDetail.htm?serverId=109&uuid={item['uuid']}&recommendId={item['recommendId']}&controlType=",
                    "date": item["recomTimeStr"],
                    "source": "能源知识服务平台"
                }
                for item in data["data"]["data"]
            ]
        
        except Exception as e:
            print(f"解析失败: {str(e)}")
            return []
    
    def get_next_page(self, html):
        """获取下一页参数"""
        try:
            data = json.loads(html)
            current_page = data['data']['pageNumber']
            # print(f"当前页: {current_page}")
            total_page = data['data']['pageSize']
            
            if current_page < total_page:
                # 构建下一页的URL
                next_page_url = self.base_url.replace(f"page={current_page}", f"page={current_page + 1}")
                self.base_url = next_page_url
                # print(f"下一页URL: {next_page_url}")
                return next_page_url
            return None
        except:
            return None

    def fetch_page(self, url=None, data=None):
        """重写获取方法以支持分页"""
        target_url = url or self.base_url
        
        try:
            response = requests.get(
                target_url,
                headers=self.headers,
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
            
        except Exception as e:
            print(f"请求失败: {e}")
            return None
