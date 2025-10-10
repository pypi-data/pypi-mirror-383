# encoding: utf-8
import asyncio
import time
import ssl
import random
from typing import Any, Dict, Union
from curl_cffi.requests import BrowserType, RequestsError, AsyncSession

from . import proxy as proxy_client
from ..lib import logger
from ..exception.exceptions import ProxyGetFailException, RetryRequest

LOGGER = logger.get('CFFI请求')


class SSLFactory:
    ciphers = ('ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
               'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES').split(":")

    @staticmethod
    def gen() -> ssl.SSLContext:
        random.shuffle(SSLFactory.ciphers)
        ciphers = ":".join(SSLFactory.ciphers)
        ciphers = ciphers + ":!aNULL:!eNULL:!MD5"
        context = ssl.create_default_context()
        context.set_ciphers(ciphers)
        return context


class CffiClient:

    def __init__(
            self,
            timeout: Union[float, tuple] = None,
            headers=None,
            ssl_context: ssl.SSLContext = None,
            allow_redirects: bool = True,
            enable_proxy: bool = True,
            proxy_protocol: str = 'http',
            session: AsyncSession = None
    ):
        self.timeout = timeout
        self.headers = headers
        self.ssl_context = ssl_context or SSLFactory.gen()
        self.allow_redirects = allow_redirects
        # 全局启用代理
        self.enable_proxy = enable_proxy

        # 代理
        self.proxy = None
        self.proxy_protocol = proxy_protocol or 'http'
        # 会话
        self.session = None
        self.ensure_session(session)

        self.enum_list = list()
        for tuple_item in BrowserType.__members__.items():
            self.enum_list.append(tuple_item[1])

    async def get(
            self, url, *,
            params: Any = None, timeout: Union[float, tuple] = None,
            cookies: Dict = None, headers: Dict = None, allow_redirects: bool = True,
            enable_proxy: Union[bool] = None, impersonate: str = None, verify: bool = True, proxy: Any = None
    ):
        try:
            # 会话
            self.ensure_session()
            # 代理配置
            if proxy:
                _proxy = proxy
            else:
                _enable_proxy = self.enable_proxy
                if enable_proxy is not None:
                    _enable_proxy = enable_proxy
                if _enable_proxy and not self.proxy:
                    await self.init_proxy(_enable_proxy)
                _proxy = self.proxy
                if not _enable_proxy:
                    _proxy = None

            start = time.time()
            _impersonate = random.choice(self.enum_list)
            return await self.session.get(
                url=url, params=params,
                headers=headers, cookies=cookies, proxy=_proxy,
                allow_redirects=allow_redirects, timeout=timeout, impersonate=impersonate, verify=verify
            )
        except (ProxyGetFailException, RequestsError) as tme:
            LOGGER.info(f"超时[{self.proxy}]: {type(tme)}")
            raise RetryRequest(ex=tme)
        except Exception as e:
            LOGGER.info(f"异常[{self.proxy}]: {type(e)}")
            raise e

    async def post(
            self, url, *,
            data: Any = None, json: Any = None, params: Any = None, timeout: Union[float, tuple] = None,
            cookies: Dict = None, headers: Dict = None, allow_redirects: bool = True,
            enable_proxy: Union[bool] = None, impersonate: str = None, verify: bool = True
    ):
        try:
            # 会话
            self.ensure_session()

            # 代理配置
            _enable_proxy = self.enable_proxy
            if enable_proxy is not None:
                _enable_proxy = enable_proxy
            if _enable_proxy and not self.proxy:
                await self.init_proxy(_enable_proxy)
            _proxy = self.proxy
            if not _enable_proxy:
                _proxy = None

            start = time.time()
            _impersonate = random.choice(self.enum_list)
            return await self.session.get(
                url=url, params=params, data=data, json=json,
                headers=headers, cookies=cookies, proxy=_proxy,
                allow_redirects=allow_redirects, timeout=timeout, impersonate=impersonate, verify=verify
            )
        except (ProxyGetFailException, RequestsError) as tme:
            LOGGER.info(f"超时[{self.proxy}]: {type(tme)}")
            raise RetryRequest(tme)
        except Exception as e:
            LOGGER.info(f"异常[{self.proxy}]: {type(e)}")
            raise e

    async def options(
            self, url, *,
            data: Any = None, json: Any = None, params: Any = None, timeout: Union[float, tuple] = None,
            cookies: Dict = None, headers: Dict = None, allow_redirects: bool = True,
            enable_proxy: Union[bool] = None, impersonate: str = None, verify: bool = True
    ):
        try:
            # 会话
            self.ensure_session()

            # 代理配置
            _enable_proxy = self.enable_proxy
            if enable_proxy is not None:
                _enable_proxy = enable_proxy
            if _enable_proxy and not self.proxy:
                await self.init_proxy(_enable_proxy)
            _proxy = self.proxy
            if not _enable_proxy:
                _proxy = None

            start = time.time()
            _impersonate = random.choice(self.enum_list)
            return await self.session.options(
                url=url, params=params, data=data, json=json,
                headers=headers, cookies=cookies, proxy=_proxy,
                allow_redirects=allow_redirects, timeout=timeout, impersonate=impersonate, verify=verify
            )
        except (ProxyGetFailException, RequestsError) as tme:
            LOGGER.info(f"超时[{self.proxy}]: {type(tme)}")
            raise RetryRequest(tme)
        except Exception as e:
            LOGGER.info(f"异常[{self.proxy}]: {type(e)}")
            raise e

    async def reset_proxy(self):
        if self.enable_proxy and self.proxy:
            _proxy = self.proxy
            try:
                self.proxy = None
                await proxy_client.remove_proxy(_proxy.replace(f'{self.proxy_protocol}://', ''))
            except Exception as e:
                LOGGER.info(f"代理移除异常[{_proxy}]: {type(e)}")

    # 初始化session
    def ensure_session(self, session: AsyncSession = None):
        if not self.session:
            self.session = session or AsyncSession(
                timeout=self.timeout,
                headers=self.headers,
                loop=asyncio.get_event_loop()
            )

    async def init_proxy(self, enable_proxy: bool):
        if enable_proxy and not self.proxy:
            _proxy = await proxy_client.get_proxy()
            if not _proxy:
                # 代理加载失败时抛出异常，终止请求（不允许无代理请求）
                raise ProxyGetFailException()
            self.proxy = f'{self.proxy_protocol}://{_proxy}'

    # 关闭client
    async def close(self):
        try:
            if self.session:
                await self.session.close()
        except Exception as e:
            LOGGER.error(f'会话关闭异常: {type(e)}')
        finally:
            self.session = None
