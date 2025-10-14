import aiohttp
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class RestAPIClient:
    """
    Generic REST API client skeleton.

    - `request(...)`:
        * GET   → params in query string
        * POST  → JSON body by default
        * Any   → if `data` is provided, it is sent verbatim as the body
                  (useful for form-encoded bodies like Bybit v5)
    - `signed_request(...)`:
        * Same as above but without automatic signing; callers provide headers
        * Accepts optional `data` body (str/bytes/dict) for signed POST/PUT/DELETE
    """


    async def _handle_response(self, response: aiohttp.ClientResponse):
        """
        Basic response handler.

        Raises an exception if the HTTP status is not 200, including
        the response body for debugging. Otherwise, returns parsed JSON.
        """
        try:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"[HTTP {response.status}] Error: {text}")
            return await response.json()
        except Exception as err:
            raise err

    async def request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int = 10,
        *,
        data: Any = None,  # NEW: explicit body (e.g., form-encoded string)
    ):
        """
        Send a generic HTTP request.

        - GET requests will include `params` in the query string.
        - POST requests will send `params` as JSON payload by default.
        - If `data` is provided (str/bytes/dict), it is sent as the raw body and
          no JSON payload is added (caller controls Content-Type).
        """
        params = params or {}
        headers = headers or {"Content-Type": "application/json"}

        # 使用 aiohttp.ClientSession 作為 context manager 來自動管理 session
        async with aiohttp.ClientSession() as session:
            try:
                is_get = method.upper() == "GET"
                is_post_like = method.upper() in ("POST", "PUT", "DELETE", "PATCH")

                async with session.request(
                    method=method.upper(),
                    url=url,
                    params=params if is_get else None,
                    json=None if (data is not None) else (params if (is_post_like and params) else None),
                    data=data,  # may be None; if str/bytes provided, sent as-is
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as resp:
                    return await self._handle_response(resp)
            except Exception as e:
                raise Exception(f"[{method}] request to {url} failed: {e!r}") from e

    async def signed_request(
        self,
        method: str,
        url: str,
        headers: dict,
        timeout: int = 10,
        *,
        data: Any = None,  # NEW: pass signed bodies (e.g., x-www-form-urlencoded)
    ):
        """
        Send an authenticated HTTP request.

        Callers should:
        - Build/query-string into `url` for signed GETs (if needed).
        - Provide `headers` with auth/signature.
        - Provide `data` for POST/PUT/DELETE if a body must be signed/sent
          (e.g., Bybit v5 form body). Content-Type is NOT overridden here.
        """
        # 使用 aiohttp.ClientSession 作為 context manager 來自動管理 session
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    data=data,  # may be None
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as resp:
                    return await self._handle_response(resp)
            except Exception as e:
                raise Exception(f"[{method}] request to {url} failed: {e!r}") from e

