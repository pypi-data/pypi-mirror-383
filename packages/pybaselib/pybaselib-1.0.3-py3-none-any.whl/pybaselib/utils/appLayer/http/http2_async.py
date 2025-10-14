# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/10/13 20:01
import httpx


class AsyncHttp2Client:
    """
    一个完全异步的HTTP客户端，基于 httpx.AsyncClient。
    """

    def __init__(self, base_url: str, timeout: int = 10, headers=None):
        self.base_url = base_url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        # OPTIMIZATION: 使用 httpx.AsyncClient 替代同步的 Client
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout, verify=False, http2=True)

    def remove_header(self, key: str):
        self.headers.pop(key, None)

    # OPTIMIZATION: 所有网络请求方法都改为 async def
    async def get(self, endpoint: str, params: dict = None, headers: dict = None) -> dict:
        response = await self.client.get(endpoint, params=params, headers=self._merge_headers(headers))
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return response.text

    async def post(self, endpoint: str, data: dict = None, json: dict = None, files=None, headers: dict = None) -> dict:
        response = await self.client.post(endpoint, data=data, json=json, files=files,
                                          headers=self._merge_headers(headers))
        response.raise_for_status()
        return await self._handle_response(response)

    async def put(self, endpoint: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        response = await self.client.put(endpoint, data=data, json=json, headers=self._merge_headers(headers))
        response.raise_for_status()
        return await self._handle_response(response)

    async def patch(self, endpoint: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        response = await self.client.patch(endpoint, data=data, json=json, headers=self._merge_headers(headers))
        response.raise_for_status()
        return await self._handle_response(response)

    async def delete(self, endpoint: str, headers: dict = None) -> dict:
        response = await self.client.delete(endpoint, headers=self._merge_headers(headers))
        response.raise_for_status()
        return response.json()

    # OPTIMIZATION: 提供一个异步关闭方法
    async def aclose(self):
        """
        异步关闭 HTTP 客户端。
        """
        await self.client.aclose()

    def _merge_headers(self, headers):
        if headers:
            merged_headers = self.headers.copy()
            merged_headers.update(headers)
            return merged_headers
        return self.headers

    @staticmethod
    async def _handle_response(response):
        if response.status_code // 100 == 2:
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            response.raise_for_status()