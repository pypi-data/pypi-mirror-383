# encoding: utf-8
import asyncio
import json
import random
import threading
import time
import traceback
import aiohttp
from abc import ABC, abstractmethod
from aiohttp import ClientConnectorError, ServerDisconnectedError
from curl_cffi import requests
from ..exception.exceptions import RetryRequest
from ..lib import cfg, logger, notify, settings

from ..utils.decator import singleton

LOGGER = logger.get('代理')


class Proxy(ABC):
    def __init__(self, plat_code: str = None, supplier_code: str = None):
        self.plat_code = plat_code
        self.supplier_code = supplier_code
        self.pool = dict()  #
        self.min_pool_size = 3
        self._instance_lock = threading.Lock()
        self._last_load_time = 0
        self.min_reload_period = 5
        self.proxy_amount_pre_load = 1
        self.pool_url = f'http://fast.proxy.zcbot.cn/api/proxy/get/jd.sku_stock_pc_v1/1?mode=FI_FO'

    async def get_dynamic_proxy(self):
        """获取代理"""
        key = f"{self.plat_code}_{self.supplier_code}"

        # 检查是否需要加载代理
        if key not in self.pool or len(self.pool[key]) < self.min_pool_size:
            await self.reload(plat_code=self.plat_code, supplier_code=self.supplier_code)

        return random.choice(self.pool[key]) if key in self.pool else None

    async def reset_dynamic_proxy(self):
        """重置代理"""
        key = f"{self.plat_code}_{self.supplier_code}"
        if key in self.pool:
            self.pool[key] = []
            LOGGER.info("重置代理池: %s", key)

    async def remove_dynamic_proxy(self, plat_code: str = None, supplier_code: str = None, proxy: str = None):
        """移除代理"""
        key = f"{plat_code}_{supplier_code}"
        if key in self.pool and proxy in self.pool[key]:
            self.pool[key].remove(proxy)
            LOGGER.info("移除代理: %s", proxy)

        # 代理数量不足，触发加载
        if key not in self.pool or len(self.pool[key]) < self.min_pool_size:
            await self.reload(plat_code=plat_code, supplier_code=supplier_code)

    async def reload(self, plat_code: str = None, supplier_code: str = None):
        """提取代理"""
        key = f"{plat_code}_{supplier_code}"
        self._instance_lock.acquire(timeout=30)

        # 如果代理数量充足，则无需加载
        if key in self.pool and len(self.pool[key]) >= self.min_pool_size:
            self._instance_lock.release()
            LOGGER.info("无需加载代理: %s", len(self.pool[key]))
            return

        # 防止提取代理频率过高
        if (int(time.time()) - self._last_load_time) <= self.min_reload_period:
            time.sleep(5)

        # 提取代理(json格式返回)
        response = requests.get(self.pool_url, timeout=5, headers={'accept': 'application/json'})
        if response.status_code == 200 and response.text:
            rows = json.loads(response.text).get('data', [])
            if key not in self.pool:
                self.pool[key] = []

            for row in rows:
                ip_port = row.strip()
                if ip_port:
                    self.pool[key].append(ip_port)
                else:
                    LOGGER.error("代理数据异常: %s", row)

            self._last_load_time = int(time.time())
            LOGGER.info("加载代理: current=%s, total=%s", rows, len(self.pool[key]))
        else:
            # 异常情况
            time.sleep(10)
            LOGGER.error("代理提取异常: %s", response.text)

        self._instance_lock.release()
        return len(self.pool.get(key, [])) > 0


@singleton
class StaticProxy(Proxy):
    """长效静态代理"""

    def __init__(self, plat_code: str = None, supplier_code: str = None):
        super().__init__(plat_code, supplier_code)
        self.plat_code = plat_code
        self.supplier_code = supplier_code
        self.static_proxy = None

    async def get_proxy(self, plat_code: str = None, supplier_code: str = None):
        """获取代理"""
        if not self.static_proxy:
            await self._fetch_static_proxy(plat_code, supplier_code)

        return self.static_proxy

    async def reset_proxy(self, plat_code: str = None, supplier_code: str = None, proxy: str = None):
        """重置代理"""
        self.static_proxy = None

    # TODO 这里要根据业务改造查询和解析方式
    async def _fetch_static_proxy(self, plat_code: str = None, supplier_code: str = None):
        """获取代理配置信息"""
        _plat_code = plat_code or self.plat_code
        _supplier_code = supplier_code or self.supplier_code

        try:
            # 接口请求参数
            params = {
                'plat_code': _plat_code,
                'supplier_code': _supplier_code
            }
            api = cfg.get('ACCOUNT_PROXY_FETCH_API', '')
            async with aiohttp.ClientSession() as session:
                async with session.post(api, json=params) as rs:
                    if rs.status == 200:
                        js_data = await rs.json() or {}
                        proxy = js_data.get("data", '')
                        if proxy:
                            LOGGER.info(f"获取静态代理成功: proxy={proxy}, plat_code={_plat_code}, supplier_code={_supplier_code}")
                            self.static_proxy = proxy
                    else:
                        LOGGER.info(f"获取静态代理失败:{rs.text}")
        except (asyncio.exceptions.TimeoutError, ClientConnectorError, ServerDisconnectedError) as tme:
            LOGGER.info(f"--> 提取超时: plat_code={_plat_code}, supplier_code={_supplier_code}, e={type(tme)}")
            raise RetryRequest(tme)
        except Exception as e:
            LOGGER.error(f"--> 提取异常: plat_code={_plat_code}, supplier_code={_supplier_code}, e={traceback.format_exc()}")
            raise e

    # TODO 这里要根据业务改造请求和解析方式
    async def _lock_static_proxy(self, plat_code: str = None, supplier_code: str = None, proxy: str = None):
        """禁用代理配置信息"""
        _plat_code = plat_code or self.plat_code
        _supplier_code = supplier_code or self.supplier_code

        try:
            # 接口请求参数
            params = {
                'plat_code': _plat_code,
                'supplier_code': _supplier_code
            }
            api = cfg.get('ACCOUNT_PROXY_LOCK_API', 'xxxx')
            async with aiohttp.ClientSession() as session:
                async with session.get(api, params=params) as rs:
                    if rs.status == 200:
                        js_data = await rs.json() or {}
                        proxy = js_data.get("data", '')
                        if proxy:
                            LOGGER.info(f"静态代理重置成功: proxy={proxy}, plat_code={_plat_code}, supplier_code={_supplier_code}")
                            self.static_proxy = proxy

                    LOGGER.info(f"获取静态代理失败:{rs.text}")
        except (asyncio.exceptions.TimeoutError, ClientConnectorError, ServerDisconnectedError) as tme:
            LOGGER.info(f"--> 提取超时: plat_code={_plat_code}, supplier_code={_supplier_code}, e={type(tme)}")
            raise RetryRequest(tme)
        except Exception as e:
            LOGGER.error(f"--> 提取异常: plat_code={_plat_code}, supplier_code={_supplier_code}, e={traceback.format_exc()}")
            raise e
