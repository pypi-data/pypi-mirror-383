"""
通用客户端
提供简洁的数据查询接口
"""
import pandas as pd
import json
import requests
from functools import partial
from typing import Optional, Dict, Any
from datacenter_common.schemas import ResultType


class DataApi:
    """
    简洁通用数据API客户端

    使用方式：
    ```python
    import datacenter_client as dc

    # 初始化客户端
    client = dc.api(token='your_token', base_url='http://localhost:10000')

    # 查询HSGT分页数据
    df = client.hsgt_page_list(page=1, page_size=20)

    # 查询指定字段的HSGT分页数据
    df = client.hsgt_page_list(page=1, page_size=10, fields='trade_date,stock_code,stock_name,hold_market_cap')

    # 按股票代码查询HSGT数据
    df = client.hsgt_by_stock(stock_code='00700.HK', limit=50)

    # 按股票代码查询并指定字段
    df = client.hsgt_by_stock(stock_code='00700.HK', limit=10, fields='trade_date,stock_code,stock_name,hold_market_cap')
    ```
    """

    def __init__(self, token: str, base_url: str = 'http://localhost:10000', timeout: int = 30):
        """
        初始化客户端

        Args:
            token: API认证token
            base_url: API服务基础URL
            timeout: 请求超时时间
        """
        self.__token = token
        self.__base_url = base_url.rstrip('/')
        self.__timeout = timeout
        self.__dataapi_url = f"{self.__base_url}/api/v1/dataapi"

    def query(self, api_name: str, fields: str = '', **kwargs) -> pd.DataFrame:
        """
        通用查询方法，与tushare的query方法完全一致

        Args:
            api_name: API名称，如'hsgt_south_fund'
            fields: 需要返回的字段，逗号分隔，如'trade_date,stock_code,stock_name'
            **kwargs: 查询参数

        Returns:
            pd.DataFrame: 查询结果
        """
        # 扁平化参数格式，与API期望格式一致
        req_params = kwargs.copy()
        req_params['fields'] = fields

        try:
            # 发送HTTP请求
            url = f"{self.__dataapi_url}/{api_name}"
            headers = {
                'X-API-Key': self.__token,
                'Content-Type': 'application/json'
            }
            res = requests.post(url, json=req_params, headers=headers, timeout=self.__timeout)

            if res.status_code != 200:
                raise Exception(f"HTTP请求失败，状态码: {res.status_code}")

            result = res.json()

            # 检查响应状态
            if result.get('code') != 0:
                raise Exception(result.get('msg', '未知错误'))

            # 解析数据
            data = result.get('data', {})
            if not data:
                return pd.DataFrame()

            columns = data.get('fields', [])
            items = data.get('items', [])

            if not items:
                return pd.DataFrame()

            # 根据结果类型转换为DataFrame
            result_type = ResultType(result.get('result_type', 'table'))

            if result_type == ResultType.DICT:
                # 字典结果，转换为单行DataFrame
                return pd.DataFrame([data])
            elif result_type == ResultType.SINGLE:
                # 单条记录，转换为单行DataFrame
                return pd.DataFrame([data])
            elif result_type == ResultType.PAGE:
                # 分页结果，转换为DataFrame并保留分页信息
                df = pd.DataFrame(items, columns=columns)
                # 将分页信息作为属性存储
                if 'pagination' in result:
                    df._pagination = result['pagination']
                return df
            else:
                # 默认表格结果
                return pd.DataFrame(items, columns=columns)

        except requests.exceptions.Timeout:
            raise Exception(f"请求超时: {self.__timeout}秒")
        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到服务器: {self.__base_url}")
        except json.JSONDecodeError:
            raise Exception("响应数据格式错误")
        except Exception as e:
            raise Exception(f"查询失败: {str(e)}")

    def __getattr__(self, name: str):
        """
        魔术方法，动态创建API方法
        例如：pro.hsgt_south_fund() 等价于 pro.query('hsgt_south_fund')
        """
        return partial(self.query, name)


def api(token: str = '', base_url: str = 'http://localhost:10000', timeout: int = 30) -> DataApi:
    """
    初始化API客户端

    Args:
        token: API认证token
        base_url: API服务基础URL
        timeout: 请求超时时间

    Returns:
        DataApi: API客户端实例
    """
    if not token:
        raise ValueError('token不能为空')

    return DataApi(token=token, base_url=base_url, timeout=timeout)