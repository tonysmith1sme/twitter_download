import httpx
import json
import time
import requests
import bs4
from urllib.parse import urlparse, quote
from url_utils import quote_url
from transaction_generate import get_transaction_id, get_url_path

class bookmark_util():
    """
    Twitter推文书签功能
    使用specified账户为推文添加书签
    """
    
    def __init__(self, headers: dict, proxies=None, log_output=False):
        """
        初始化书签工具
        :param headers: 包含cookie和authorization的请求头
        :param proxies: 代理设置
        :param log_output: 是否输出日志
        """
        self.headers = headers.copy()  # 复制headers以避免修改原始对象
        self.proxies = proxies
        self.log_output = log_output
        self.request_count = 0
        self.success_count = 0
        self.fail_count = 0
        
        # 初始化transaction_id生成器
        try:
            self.ct = get_transaction_id()
            self.has_transaction_support = True
            if self.log_output:
                print('成功初始化X-Client-Transaction-ID生成器')
        except Exception as e:
            self.has_transaction_support = False
            if self.log_output:
                print(f'警告: 无法初始化X-Client-Transaction-ID生成器: {str(e)}')
    
    def add_bookmark(self, tweet_id: str) -> bool:
        """
        为推文添加书签
        :param tweet_id: 推文ID
        :return: 是否成功
        """
        # Twitter GraphQL BookmarkAdd endpoint (更新的endpoint ID)
        # 使用BookmarkAdd endpoint而不是CreateBookmark
        graphql_id = '-V21wukAaCGXHbUZPZ2wGw'  # BookmarkAdd endpoint ID
        url = f'https://x.com/i/api/graphql/{graphql_id}/BookmarkAdd'
        
        # 准备请求头副本
        request_headers = self.headers.copy()
        
        # 添加X-Client-Transaction-ID（如果可用）
        if self.has_transaction_support:
            try:
                path = f'/i/api/graphql/{graphql_id}/BookmarkAdd'
                transaction_id = self.ct.generate_transaction_id(method='POST', path=path)
                request_headers['x-client-transaction-id'] = transaction_id
            except Exception as e:
                if self.log_output:
                    print(f'警告: 无法生成X-Client-Transaction-ID: {str(e)}')
        
        # 准备请求体
        payload = {
            "variables": {
                "tweet_id": tweet_id
            },
            "queryId": graphql_id
        }
        
        try:
            response = httpx.post(
                url,
                headers=request_headers,
                json=payload,
                proxy=self.proxies,
                timeout=10
            )
            self.request_count += 1
            
            if response.status_code == 200:
                try:
                    result = json.loads(response.text)
                    # 检查响应中是否有数据或错误
                    if 'data' in result and result['data']:
                        # 检查是否有errors字段
                        if 'errors' not in result:
                            self.success_count += 1
                            if self.log_output:
                                print(f'推文 {tweet_id} 书签添加成功')
                            return True
                    
                    if 'errors' in result:
                        self.fail_count += 1
                        error_msg = result['errors'][0].get('message', '未知错误') if result['errors'] else '未知错误'
                        if self.log_output:
                            print(f'推文 {tweet_id} 书签添加失败: API错误 - {error_msg}')
                        return False
                    
                    # 其他成功响应
                    self.success_count += 1
                    if self.log_output:
                        print(f'推文 {tweet_id} 书签添加成功')
                    return True
                    
                except json.JSONDecodeError:
                    self.fail_count += 1
                    if self.log_output:
                        print(f'推文 {tweet_id} 书签添加失败: 响应解析错误')
                    return False
            else:
                self.fail_count += 1
                if self.log_output:
                    print(f'推文 {tweet_id} 书签添加失败: HTTP {response.status_code}')
                    if response.text:
                        try:
                            print(f'  响应: {response.text[:200]}')
                        except:
                            pass
                return False
                
        except Exception as e:
            self.fail_count += 1
            if self.log_output:
                print(f'推文 {tweet_id} 书签添加异常: {str(e)}')
            return False
    
    def batch_add_bookmarks(self, tweet_ids: list, delay: float = 0.5) -> dict:
        """
        批量添加书签
        :param tweet_ids: 推文ID列表
        :param delay: 请求间隔(秒)，默认0.5秒
        :return: 包含成功和失败统计的字典
        """
        results = {
            'total': len(tweet_ids),
            'success': 0,
            'failed': 0,
            'failed_ids': []
        }
        
        for tweet_id in tweet_ids:
            if self.add_bookmark(tweet_id):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['failed_ids'].append(tweet_id)
            
            time.sleep(delay)  # 避免请求过于频繁
        
        return results
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        :return: 包含请求次数和成功/失败次数的字典
        """
        return {
            'total_requests': self.request_count,
            'success': self.success_count,
            'failed': self.fail_count
        }
