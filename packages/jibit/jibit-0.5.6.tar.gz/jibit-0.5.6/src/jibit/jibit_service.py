import aiohttp
from typing import Optional, Dict, Tuple
from .exceptions import JibitException, JibitErrorCode
from .helpers import parse_card_shaba_response
from .models import JibitTokens,  JibitCard


class JibitService:

    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://napi.jibit.ir/ide/v1"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")

    # ---------- Token Management ----------
    async def generate_token(self) -> JibitTokens:
        url = f"{self.base_url}/tokens/generate"
        payload = {"apiKey": self.api_key, "secretKey": self.secret_key}
        data = await self._post_raw(url, payload)
        return JibitTokens(
            access_token=data["accessToken"],
            refresh_token=data["refreshToken"]
        )

    async def refresh_token(self, tokens: JibitTokens) -> JibitTokens:
        url = f"{self.base_url}/tokens/refresh"
        payload = {"accessToken": tokens.access_token, "refreshToken": tokens.refresh_token}
        data = await self._post_raw(url, payload)
        return JibitTokens(
            access_token=data["accessToken"],
            refresh_token=data["refreshToken"]
        )

    # ---------- Internal HTTP methods ----------
    async def _get(self, url: str, tokens: Optional[JibitTokens]) -> Tuple[dict, Optional[JibitTokens]]:
        return await self._request_with_token_retry("GET", url, tokens)

    async def _post(self, url: str, json_data: dict, tokens: Optional[JibitTokens]) -> Tuple[dict, Optional[JibitTokens]]:
        return await self._request_with_token_retry("POST", url, tokens, json_data=json_data)

    # ---------- Core Token Retry Logic ----------
    async def _request_with_token_retry(
        self,
        method: str,
        url: str,
        tokens: Optional[JibitTokens],
        json_data: Optional[dict] = None,
        _retry: bool = True
    ) -> Tuple[dict, Optional[JibitTokens]]:
        headers = {"Authorization": f"Bearer {tokens.access_token}"} if tokens else {}

        try:
            if method == "GET":
                data = await self._get_raw(url, headers)
            else:
                data = await self._post_raw(url, json_data, headers)
            return data, None

        except JibitException as e:
            if (e.code == JibitErrorCode.UNAUTHORIZED or e.code == JibitErrorCode.FORBIDDEN) and _retry:
                new_tokens = None
                if tokens:
                    try:
                        new_tokens = await self.refresh_token(tokens)
                    except JibitException as refresh_error:
                        if refresh_error.code != JibitErrorCode.UNAUTHORIZED:
                            raise

                if not new_tokens:
                    new_tokens = await self.generate_token()

                return await self._request_with_token_retry(
                    method, url, new_tokens, json_data, _retry=False
                )

            raise

    # ---------- Low-level HTTP calls ----------
    async def _get_raw(self, url: str, headers: Optional[Dict]) -> dict:
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    return await self._handle_response(resp)
        except aiohttp.ClientConnectionError:
            raise JibitException(JibitErrorCode.SERVICE_UNAVAILABLE, "Connection failed", http_status=503)

    async def _post_raw(self, url: str, json_data: dict, headers: Optional[Dict] = None) -> dict:
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=json_data, headers=headers) as resp:
                    return await self._handle_response(resp)
        except aiohttp.ClientConnectionError:
            raise JibitException(JibitErrorCode.SERVICE_UNAVAILABLE, "Connection failed", http_status=503)

    # ---------- Response handler ----------
    async def _handle_response(self, resp: aiohttp.ClientResponse) -> dict:
        """Handle API responses and convert to JibitExceptions when needed."""
        try:
            content = await resp.json(content_type=None)
        except Exception:
            content = await resp.text()

        code = content.get("code") if isinstance(content, dict) else None

        if code:
            error_code = JibitErrorCode.from_code(code)
            if error_code != JibitErrorCode.UNKNOWN_ERROR:
                raise JibitException(code=error_code,http_status=resp.status)

        status_map = {
            401: (JibitErrorCode.UNAUTHORIZED, "Token invalid or expired"),
            403: (JibitErrorCode.UNAUTHORIZED, "Forbidden"),
            500: (JibitErrorCode.SERVICE_UNAVAILABLE, "Jibit internal error"),
            503: (JibitErrorCode.SERVICE_UNAVAILABLE, "Service unavailable"),
        }

        if resp.status in status_map:
            code, msg = status_map[resp.status]
            raise JibitException(code, msg, http_status=resp.status)

        if resp.status not in (200, 201):
            raise JibitException(
                JibitErrorCode.UNKNOWN_ERROR,
                f"Unexpected status {resp.status}: {content}",
                http_status=resp.status,
            )

        if not isinstance(content, dict):
            raise JibitException(
                JibitErrorCode.UNKNOWN_ERROR, f"Non-JSON response: {content}", resp.status
            )

        return content

    # ---------- Public APIs ----------
    async def card_to_iban(
        self, card_number: str, tokens: Optional[JibitTokens]
    ) -> Tuple[JibitCard, Optional[JibitTokens]]:
        url = f"{self.base_url}/cards?number={card_number}&iban=true"
        data, new_tokens = await self._get(url, tokens)
        return parse_card_shaba_response(data), new_tokens

    async def match_iban_to_national(self,tokens: Optional[JibitTokens], iban: str, national: str, birth_date: str)-> Tuple[bool, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/matching?iban={iban}&nationalCode={national}&birthDate={birth_date}"
        data, new_tokens = await self._get(url, tokens)
        matched = data.get('matched',False)
        return matched, new_tokens