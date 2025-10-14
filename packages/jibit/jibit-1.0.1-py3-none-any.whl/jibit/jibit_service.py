import aiohttp
from typing import Optional, Dict, Tuple, Any, Coroutine, List, Annotated

from src.jibit import JibitTokens
from src.jibit.models import ForeignerIdentityInfo, CorporationIdentityInfo, militaryServiceQualificationInfo, SanaInfo, \
    Balance
from .exceptions import JibitException, JibitErrorCode
from .helpers import parse_card_shaba_response, parse_postal_to_address_response, parse_postal_wsginfo_response, \
    parse_identity_similarity_response, parse_identity_foreigners_response, parse_identity_corporation_response, \
    parse_military_qualification_info, parse_sana_info, parse_balances
from .models import JibitTokens, JibitCard, BankIdentify, AddressInfo, WgsInfo, IdentitySimilarity


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

    # ---------- TESTED Public APIs ----------

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

    # ---------- NOT TESTED Public APIs ----------

    async def match_deposit_number_to_national(self,tokens: Optional[JibitTokens], bank_identify: BankIdentify, deposit_number: str, national: str, birth_date: str)-> Tuple[bool, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/matching?bank={bank_identify}&depositNumber={deposit_number}&nationalCode={national}&birthDate={birth_date}"
        data, new_tokens = await self._get(url, tokens)
        matched = data.get('matched',False)
        return matched, new_tokens

    async def match_card_to_national(self,tokens: Optional[JibitTokens],  card_number: str, national: str, birth_date: str)-> Tuple[bool, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/matching?cardNumber={card_number}&nationalCode={national}&birthDate={birth_date}"
        data, new_tokens = await self._get(url, tokens)
        matched = data.get('matched',False)
        return matched, new_tokens

    async def match_iban_to_name(self,tokens: Optional[JibitTokens],  iban: str, name: str)-> Tuple[bool, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/matching?iban={iban}&name={name}"
        data, new_tokens = await self._get(url, tokens)
        matched = data.get('matched',False)
        return matched, new_tokens

    async def match_card_to_name(self,tokens: Optional[JibitTokens],  card_number: str, name: str)-> Tuple[bool, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/matching?cardNumber={card_number}&name={name}"
        data, new_tokens = await self._get(url, tokens)
        matched = data.get('matched',False)
        return matched, new_tokens

    async def match_deposit_number_to_name(self,tokens: Optional[JibitTokens],  bank_identify: BankIdentify, deposit_number: str, name: str)-> Tuple[bool, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/matching?bank={bank_identify}&depositNumber={deposit_number}&name={name}"
        data, new_tokens = await self._get(url, tokens)
        matched = data.get('matched',False)
        return matched, new_tokens

    async def match_national_to_number(self,tokens: Optional[JibitTokens],  national: str, mobile: str)-> Tuple[bool, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/matching?nationalCode={national}&mobileNumber={mobile}"
        data, new_tokens = await self._get(url, tokens)
        matched = data.get('matched',False)
        return matched, new_tokens

    async def postal_to_address(self,tokens: Optional[JibitTokens],  postal_code: str)-> Tuple[AddressInfo, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/postal?code={postal_code}"
        data, new_tokens = await self._get(url, tokens)
        return parse_postal_to_address_response(data), new_tokens

    async def postal_to_wgsinfo(self,tokens: Optional[JibitTokens],  postal_code: str)-> Tuple[WgsInfo, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/postal/wgs?code={postal_code}"
        data, new_tokens = await self._get(url, tokens)
        return parse_postal_wsginfo_response(data), new_tokens

    async def identity_similarity(self,tokens: Optional[JibitTokens], national_code:str,birth_date:str,first_name:str,last_name:str,full_name:str,father_name:str) -> Tuple[IdentitySimilarity, Optional[JibitTokens]]:
        url = f"{self.base_url}/services/identity/similarity?nationalCode={national_code}&birthDate={birth_date}&firstName={first_name}&lastName={last_name}&fullName={full_name}&fatherName={father_name}"
        data, new_tokens = await self._get(url, tokens)
        return parse_identity_similarity_response(data), new_tokens

    async def identity_foreigners(self,tokens: Optional[JibitTokens], fida:str,) -> tuple[ForeignerIdentityInfo, JibitTokens | None]:
        url = f"{self.base_url}/services/foreigners/identity?fida={fida}"
        data, new_tokens = await self._get(url, tokens)
        return parse_identity_foreigners_response(data), new_tokens

    async def identity_corporation(self,tokens: Optional[JibitTokens], code:str,) -> tuple[CorporationIdentityInfo, JibitTokens | None]:
        url = f"{self.base_url}/services/corporation/identity?code={code}"
        data, new_tokens = await self._get(url, tokens)
        return parse_identity_corporation_response(data), new_tokens

    async def military_qualification_info(self,tokens: Optional[JibitTokens], national_code:str,) -> tuple[militaryServiceQualificationInfo, JibitTokens | None]:
        url = f"{self.base_url}/services/social/msq?nationalCode={national_code}"
        data, new_tokens = await self._get(url, tokens)
        return parse_military_qualification_info(data), new_tokens

    async def sana_info(self,tokens: Optional[JibitTokens], national_code:str,mobile:str,) -> tuple[SanaInfo, JibitTokens | None]:
        url = f"{self.base_url}/services/social/sana?nationalCode={national_code}&mobileNumber={mobile}"
        data, new_tokens = await self._get(url, tokens)
        return parse_sana_info(data), new_tokens


    # ---------- Account APIs ----------

    async def account_balances(self,tokens: Optional[JibitTokens]) -> tuple[List[Balance], JibitTokens | None]:
        url = f"{self.base_url}/balances"
        data, new_tokens = await self._get(url, tokens)
        return parse_balances(data), new_tokens

    # TODO: Complete
    async def account_reports_daily(self,tokens: Optional[JibitTokens],year:Annotated[str, "2-digit year, e.g. '00 for 1400'"],month:Annotated[str, "2-digit month (01-12)"],day:Annotated[str, "2-digit day (01-31)"]):
        pass
        """
        :param
            tokens Optional[JibitTokens] : jibit tokens
            year (str): 2-digit year, e.g. '25'
            month (str): 2-digit month (01–12)
            day (str): 2-digit day (01–31)
        """
        url = f"{self.base_url}/reports/daily?yearMonthDay={year}{month}{day}"
        # data, new_tokens = await self._get(url, tokens)
        # return parse_reports_daily(data), new_tokens
