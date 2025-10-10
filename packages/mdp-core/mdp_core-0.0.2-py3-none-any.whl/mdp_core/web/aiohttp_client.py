# encoding: utf-8
import asyncio
import time
import ssl
import random
from asyncio import StreamReader
from typing import Any, Optional, Dict, Union
from aiohttp import TCPConnector, ClientSession, ClientConnectorError, ServerDisconnectedError, ClientTimeout, ClientResponse
from aiohttp.typedefs import JSONDecoder, DEFAULT_JSON_DECODER
from mdp_core.lib import logger
from mdp_core.exception.exceptions import ProxyGetFailException, RetryRequest
from mdp_core.web import proxy as proxy_client

LOGGER = logger.get('异步请求')

# 默认超时配置
DEFAULT_TIMEOUT = ClientTimeout(
    total=5,
    connect=5,
    sock_connect=1,
    sock_read=5
)


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


class HttpClientResponse:

    def __init__(self, response: ClientResponse, seconds_cost: float = None):
        self.response = response
        self._seconds_cost = seconds_cost

    @property
    def url(self) -> str:
        return str(self.response.url)

    @property
    def status_code(self) -> int:
        return self.response.status

    @property
    def cookies(self) -> Dict:
        return self.response.cookies

    @property
    def content(self) -> StreamReader:
        return self.response._body

    @property
    def text(self, default: Any = None, encoding: Optional[str] = None, errors: str = "strict") -> str:
        if self.response._body:
            if encoding is None:
                encoding = self.response.get_encoding()
            return self.response._body.decode(  # type: ignore[no-any-return,union-attr]
                encoding, errors=errors
            )

        return default or ''

    def json(self, default: Any = None, *, encoding: Optional[str] = None, loads: JSONDecoder = DEFAULT_JSON_DECODER) -> Any:
        if self.response._body:
            stripped = self.response._body.strip()  # type: ignore[union-attr]
            if not stripped:
                return None
            if encoding is None:
                encoding = self.response.get_encoding()
            return loads(stripped.decode(encoding))

        return default or {}

    def total_seconds(self) -> float:
        return self._seconds_cost or -1


class HttpClient:

    def __init__(
            self,
            timeout: Union[float, ClientTimeout] = None,
            headers=None,
            ssl_context: ssl.SSLContext = None,
            allow_redirects: bool = True,
            enable_proxy: bool = True,
            proxy_protocol: str = 'http',
            session: ClientSession = None
    ):
        self.timeout = self._timeout(timeout)
        self.headers = headers
        self.ssl_context = ssl_context or SSLFactory.gen()
        self.allow_redirects = allow_redirects

        # 全局启用代理
        self.enable_proxy = enable_proxy
        self.proxy = None
        self.proxy_protocol = proxy_protocol or 'http'

        # 会话
        self.session = None
        self.ensure_session(session)

    async def get(
            self, url, *,
            params: Any = None, timeout: Union[float, ClientTimeout] = None,
            cookies: Dict = None, headers: Dict = None, allow_redirects: bool = True,
            enable_proxy: Union[bool] = None
    ) -> HttpClientResponse:
        try:
            # 会话verify
            self.ensure_session()

            # 代理配置
            _enable_proxy = self.enable_proxy and enable_proxy
            if _enable_proxy and not self.proxy:
                await self.init_proxy(_enable_proxy)
            _proxy = self.proxy
            if not _enable_proxy:
                _proxy = None

            start = time.time()
            async with self.session.get(
                    url=url, params=params,
                    headers=headers, cookies=cookies, proxy=_proxy,
                    allow_redirects=allow_redirects, timeout=self._timeout(timeout)
            ) as resp:
                await resp.read()
                return HttpClientResponse(response=resp, seconds_cost=(time.time() - start))
        except (ProxyGetFailException, asyncio.exceptions.TimeoutError, ClientConnectorError, ServerDisconnectedError) as tme:
            LOGGER.info(f"超时[{self.proxy}]: {type(tme)}")
            raise RetryRequest(tme)
        except Exception as e:
            LOGGER.info(f"异常[{self.proxy}]: {type(e)}")
            raise e

    async def post(
            self, url, *,
            data: Any = None, json: Any = None, params: Any = None, timeout: Union[float, tuple, ClientTimeout] = None,
            cookies: Dict = None, headers: Dict = None, allow_redirects: bool = True,
            enable_proxy: Union[bool] = None
    ) -> HttpClientResponse:
        try:
            # 会话
            self.ensure_session()

            # 代理配置
            _enable_proxy = self.enable_proxy and enable_proxy
            if _enable_proxy and not self.proxy:
                await self.init_proxy(_enable_proxy)
            _proxy = self.proxy
            if not _enable_proxy:
                _proxy = None

            start = time.time()
            async with self.session.post(
                    url=url, data=data, json=json, params=params,
                    headers=headers, cookies=cookies, proxy=_proxy,
                    allow_redirects=allow_redirects, timeout=timeout
            ) as resp:
                await resp.read()
                return HttpClientResponse(response=resp, seconds_cost=(time.time() - start))
        except (ProxyGetFailException, asyncio.exceptions.TimeoutError, ClientConnectorError, ServerDisconnectedError) as tme:
            LOGGER.info(f"超时[{self.proxy}]: {type(tme)}")
            raise RetryRequest(tme)
        except Exception as e:
            LOGGER.info(f"异常[{self.proxy}]: {type(e)}")
            raise e

    async def init_proxy(self, enable_proxy: bool):
        if enable_proxy and not self.proxy:
            _proxy = await proxy_client.get_proxy()
            if not _proxy:
                # 代理加载失败时抛出异常，终止请求（不允许无代理请求）
                raise ProxyGetFailException()
            self.proxy = f'{self.proxy_protocol}://{_proxy}'

    # 重置代理
    async def reset_proxy(self):
        if self.enable_proxy and self.proxy:
            _proxy = self.proxy
            try:
                self.proxy = None
                await proxy_client.remove_proxy(_proxy.replace(f'{self.proxy_protocol}://', ''))
            except Exception as e:
                LOGGER.info(f"代理移除异常[{_proxy}]: {type(e)}")

    # 超时时间构造
    def _timeout(self, timeout: Union[float, tuple, ClientTimeout]):
        if isinstance(timeout, ClientTimeout):
            return timeout
        elif isinstance(timeout, float):
            return ClientTimeout(total=timeout)
        else:
            return DEFAULT_TIMEOUT

    # 初始化session
    def ensure_session(self, session: ClientSession = None):
        if not self.session or self.session.closed:
            self.session = session or ClientSession(
                timeout=self.timeout,
                headers=self.headers,
                connector=TCPConnector(ssl=self.ssl_context)
            )

    # 关闭client
    async def close(self):
        try:
            if self.session:
                await self.session.close()
        except Exception as e:
            LOGGER.error(f'会话关闭异常: {type(e)}')
        finally:
            self.session = None
