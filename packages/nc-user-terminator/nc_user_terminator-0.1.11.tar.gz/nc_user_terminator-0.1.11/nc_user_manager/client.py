import asyncio
from typing import Optional, Dict, Any

from .cache import MemoryCache, BaseCache, AsyncRedisCache
from .models import UserResponse, OAuth2AuthorizeResponse, CallbackResponse
from .exceptions import OAuthError
from .utils import request


PRODUCT_HEADER = "X-Product-Code"
DEFAULT_TTL = 3600


class OAuthClient:
    def __init__(
        self,
        product_code: str,
        base_url: Optional[str] = None,
        redirect_url: Optional[str] = None,
        single_session: bool = False,
        cache: Optional[BaseCache] = None,
    ):
        """
        OAuth 客户端

        :param base_url: 服务端基础地址 (例如 http://localhost:8000)
        :param product_code: 产品编码
        :param redirect_url: 可选，重定向地址
        :param single_session: 是否单会话登录
        """
        if not base_url:
            base_url = "http://172.27.92.74"
        self._base_url = base_url.rstrip("/")
        self._product_code = product_code
        self._redirect_url = redirect_url
        self._single_session = single_session
        self._cache = cache or MemoryCache(maxsize=10000, ttl=DEFAULT_TTL)
        # 异步缓存，仅允许异步 redis
        self._async_cache = self._cache.is_async

    # ----------------------
    # 内部异步包装
    # ----------------------
    async def _arequest(self, *args, **kwargs) -> dict:
        return await asyncio.to_thread(request, *args, **kwargs)

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            PRODUCT_HEADER: self._product_code,
            "Host": "auth.nc.com"
        }
        if extra:
            headers.update(extra)
        return headers

    # ----------------------
    # 授权
    # ----------------------
    def authorize(self, platform: str) -> OAuth2AuthorizeResponse:
        """同步获取授权地址"""
        params = {}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = request(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/authorize",
            params=params,
            headers=self._headers(),
        )
        return OAuth2AuthorizeResponse(res_dict)

    async def authorize_async(self, platform: str) -> OAuth2AuthorizeResponse:
        """异步获取授权地址"""
        params = {}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = await self._arequest(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/authorize",
            params=params,
            headers=self._headers(),
        )
        return OAuth2AuthorizeResponse(res_dict)

    # ----------------------
    # 普通回调
    # ----------------------
    def callback(self, platform: str, query_params: Dict[str, Any]) -> CallbackResponse:
        """同步处理 OAuth2 回调 (非 One Tap)"""
        if query_params.get("credential"):
            raise OAuthError("Use google_one_tap() for One Tap login")

        params = {"single_session": str(self._single_session).lower()}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        params.update(query_params or {})
        res_dict = request(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    async def callback_async(self, platform: str, query_params: Dict[str, Any]) -> CallbackResponse:
        """异步处理 OAuth2 回调 (非 One Tap)"""
        if query_params.get("credential"):
            raise OAuthError("Use google_one_tap_async() for One Tap login")

        params = {"single_session": str(self._single_session).lower()}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        params.update(query_params or {})
        res_dict = await self._arequest(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    # ----------------------
    # Google One Tap
    # ----------------------
    def google_one_tap(self, credential: str) -> CallbackResponse:
        """同步 Google One Tap 登录"""
        params = {
            "credential": credential,
            "single_session": str(self._single_session).lower()
        }
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = request(
            "GET",
            f"{self._base_url}/api/oauth/google/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    async def google_one_tap_async(self, credential: str) -> CallbackResponse:
        """异步 Google One Tap 登录"""
        params = {
            "credential": credential,
            "single_session": str(self._single_session).lower()
        }
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = await self._arequest(
            "GET",
            f"{self._base_url}/api/oauth/google/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    # ----------------------
    # 缓存工具
    # ----------------------
    def _cache_user(self, token: str, user_dict: dict, ttl=DEFAULT_TTL):
        key = f"user:{token}"
        self._cache.set(key, user_dict, ttl)

        if self._single_session:
            user_id = user_dict.get("id")
            if user_id:
                old_token = self._cache.get(f"user_token:{user_id}")
                if old_token and old_token != token:
                    self._cache.delete(f"user:{old_token}")
                self._cache.set(f"user_token:{user_id}", token, ttl)

    async def _cache_user_async(self, token: str, user_dict: dict, ttl=DEFAULT_TTL):
        if not self._async_cache:
            raise RuntimeError("异步缓存未配置")

        key = f"user:{token}"
        await self._cache.set(key, user_dict, ttl)

        if self._single_session:
            user_id = user_dict.get("id")
            if user_id:
                old_token = await self._cache.get(f"user_token:{user_id}")
                if old_token and old_token != token:
                    await self._cache.delete(f"user:{old_token}")
                await self._cache.set(f"user_token:{user_id}", token, ttl)

    def _uncache_user(self, token: str, user_dict: Optional[dict] = None):
        self._cache.delete(f"user:{token}")
        if self._single_session and user_dict:
            user_id = user_dict.get("id")
            if user_id:
                self._cache.delete(f"user_token:{user_id}")

    async def _uncache_user_async(self, token: str, user_dict: Optional[dict] = None):
        await self._cache.delete(f"user:{token}")
        if self._single_session and user_dict:
            user_id = user_dict.get("id")
            if user_id:
                await self._cache.delete(f"user_token:{user_id}")

    # ----------------------
    # 获取用户信息
    # ----------------------
    def say_my_name(self, token: str) -> UserResponse:
        """同步获取当前用户"""
        if self._async_cache:
            raise RuntimeError("同步缓存未配置")

        key = f"user:{token}"
        data = self._cache.get(key)
        if data:
            return UserResponse(data)

        headers = self._headers({"Authorization": f"Bearer {token}"})
        res_dict = request("GET", f"{self._base_url}/api/me", headers=headers)

        if res_dict.get("success", True):
            self._cache_user(token, res_dict)
        return UserResponse(res_dict)

    async def say_my_name_async(self, token: str) -> UserResponse:
        """异步获取当前用户"""
        key = f"user:{token}"
        if self._async_cache:
            data = await self._cache.get(key)
        else:
            data = self._cache.get(key)

        if data:
            return UserResponse(data)

        headers = self._headers({"Authorization": f"Bearer {token}"})
        res_dict = await self._arequest("GET", f"{self._base_url}/api/me", headers=headers)
        if res_dict.get("success", True):
            if self._async_cache:
                await self._cache_user_async(token, res_dict)
            else:
                self._cache_user(token, res_dict)

        return UserResponse(res_dict)

    # 刷新过期时间
    def reborn(self, token: str, extend_seconds: Optional[int] = None) -> dict:
        """重新设置过期时间"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        if extend_seconds:
            return request("POST", f"{self._base_url}/api/refresh-me", headers=headers, json_body={"extend_seconds": extend_seconds})
        else:
            return request("POST", f"{self._base_url}/api/refresh-me", headers=headers)

    async def reborn_async(self, token: str, extend_seconds: Optional[int] = None) -> dict:
        """异步重新设置过期时间"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        if extend_seconds:
            return await self._arequest("POST", f"{self._base_url}/api/refresh-me", headers=headers, json_body={"extend_seconds": extend_seconds})
        else:
            return await self._arequest("POST", f"{self._base_url}/api/refresh-me", headers=headers)

    # 登出
    def logout(self, token: str):
        headers = self._headers({"Authorization": f"Bearer {token}"})
        resp = request("POST", f"{self._base_url}/api/auth/logout", headers=headers)

        data = self._cache.get(f"user:{token}")
        self._uncache_user(token, data)
        return resp


    async def logout_async(self, token: str) -> dict:
        """异步获取当前用户"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        resp = await self._arequest("POST", f"{self._base_url}/api/auth/logout", headers=headers)

        if self._async_cache:
            data = await self._cache.get(f"user:{token}")
            await self._uncache_user_async(token, data)
        else:
            data = self._cache.get(f"user:{token}")
            self._uncache_user(token, data)
        return resp

async def main():
    def get_redis_url() -> str:
        return f'redis://default:1q2w3e@localhost:6379/1'


    import redis.asyncio as redis
    # —— Redis 连接与策略（Bearer + Redis）——
    _redis = redis.from_url(get_redis_url(), decode_responses=True)

    redis_cache = AsyncRedisCache(_redis)

    client = OAuthClient("http://auth.nc.com/", "bankgpt", "http://localhost:8000/auth/google/custom_callback", single_session=True, cache=redis_cache)
    authorize = client.authorize("google")
    print(authorize)




if __name__ == '__main__':
    asyncio.run(main())

