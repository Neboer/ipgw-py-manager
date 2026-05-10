import hashlib
import logging
import platform
from enum import Enum
from typing import Optional
from urllib.parse import quote

from requests import Session

from .sso_mobile_error import (
    MobileSSOLoginFailedError,
    MobileSSORequestFailedError,
    MobileSSOStateError,
    MobileSSOTGTExpiredError,
)

USER_AGENT = "Mozilla/5.0 (Linux; Android); com.sunyt.testdemo/3.0.11"

ENDPOINT_LOGIN_SMS = "https://personal.neu.edu.cn/prize/Front/Oauth/User/login_sms"
ENDPOINT_SMS_SEND = "https://personal.neu.edu.cn/prize/Front/Oauth/User/sms_send"
ENDPOINT_SMS_VERIFY = "https://personal.neu.edu.cn/prize/Front/Oauth/User/sms_verify"
CAS_LOGIN_URL = "https://pass.neu.edu.cn/tpass/login"

_BRAND = platform.uname().system
_DEVICE = platform.uname().machine
_HOSTNAME = platform.node()


class MobileLoginState(Enum):
    INITIAL = "INITIAL"
    SUCCESS = "SUCCESS"
    REQUIRE_SMS = "REQUIRE_SMS"
    SMS_SENT = "SMS_SENT"


class MobileSSOLoginApi:
    def __init__(self, session: Session):
        self._session = session
        self._fingerprint: Optional[str] = None
        self._sms_id: Optional[str] = None
        self.state = MobileLoginState.INITIAL

    def _generate_fingerprint(self, student_id: str) -> str:
        src = f"{_BRAND}_{_DEVICE}_{_HOSTNAME}_{student_id}"
        return hashlib.md5(src.encode()).hexdigest()

    def _request_headers(self) -> dict:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
            "X-Mobile-Device-UUID": self._fingerprint or "",
        }

    def _ensure_state(self, expected: MobileLoginState) -> None:
        if self.state != expected:
            raise MobileSSOStateError(
                f"期望状态 {expected.value}，当前状态 {self.state.value}"
            )

    def _post(self, url: str, data: dict) -> dict:
        resp = self._session.post(
            url,
            data=data,
            headers=self._request_headers(),
            allow_redirects=False,
        )
        logging.debug(f"mobile sso response [{resp.status_code}]: {resp.text}")

        if not resp.ok:
            raise MobileSSORequestFailedError(
                f"请求失败: HTTP {resp.status_code}"
            )

        try:
            return resp.json()
        except ValueError:
            raise MobileSSORequestFailedError("响应不是有效的 JSON")

    def request_login(self, student_id: str, password: str) -> Optional[str]:
        self._ensure_state(MobileLoginState.INITIAL)

        if self._fingerprint is None:
            self._fingerprint = self._generate_fingerprint(student_id)

        data = self._post(
            ENDPOINT_LOGIN_SMS,
            {
                "username": student_id,
                "password": password,
                "device_id": self._fingerprint,
            },
        )
        code = data["code"]
        msg = data.get("msg", "")
        result = data.get("result")

        if isinstance(result, list):
            if code < 0:
                raise MobileSSOLoginFailedError(msg)
            raise MobileSSORequestFailedError(msg, code)

        # result is str
        if code == 1 and isinstance(result, str) and result.startswith("TGT"):
            self.state = MobileLoginState.SUCCESS
            return result

        if code > 1:
            self.state = MobileLoginState.REQUIRE_SMS
            return None

        raise MobileSSORequestFailedError(msg, code)

    def send_sms_code(self, student_id: str, password: str) -> None:
        self._ensure_state(MobileLoginState.REQUIRE_SMS)

        data = self._post(
            ENDPOINT_SMS_SEND,
            {
                "username": student_id,
                "password": password,
                "device_id": self._fingerprint or "",
            },
        )
        code = data["code"]
        msg = data.get("msg", "")
        result = data.get("result")

        if isinstance(result, list):
            raise MobileSSORequestFailedError(msg, code)

        if code == 1 and isinstance(result, str) and len(result) > 0:
            self._sms_id = result
            self.state = MobileLoginState.SMS_SENT
            return

        raise MobileSSORequestFailedError(msg, code)

    def submit_sms_code(self, sms_code: str) -> str:
        self._ensure_state(MobileLoginState.SMS_SENT)

        if self._sms_id is None:
            raise MobileSSOStateError("短信 ID 缺失，无法提交验证码")

        data = self._post(
            ENDPOINT_SMS_VERIFY,
            {
                "sms_code": sms_code,
                "uuid": self._sms_id,
                "trust_device": "1",
                "device_id": self._fingerprint or "",
            },
        )
        code = data["code"]
        msg = data.get("msg", "")
        result = data.get("result")

        if isinstance(result, list):
            raise MobileSSORequestFailedError(msg, code)

        if code == 1 and isinstance(result, str) and result.startswith("TGT"):
            self.state = MobileLoginState.SUCCESS
            return result

        raise MobileSSORequestFailedError(msg, code)

    def exchange_tgt_for_st(self, tgt: str, service_url: str) -> str:
        """用 TGT（CASTGC）换取 CAS Service Ticket（ST）。

        向 pass.neu.edu.cn 发送 GET 请求，携带 CASTGC cookie，
        CAS 服务器验证 TGT 后 302 重定向到 service_url 并附带 ticket=ST-xxx 参数。
        返回提取的 Service Ticket 字符串。
        """
        url = f"{CAS_LOGIN_URL}?service={quote(service_url, safe='')}"
        resp = self._session.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "X-Requested-With": "com.sunyt.testdemo",
                "Cookie": f"CASTGC={tgt}",
            },
            allow_redirects=False,
        )
        logging.debug(
            f"tgt exchange [{resp.status_code}]: Location={resp.headers.get('Location', 'N/A')}"
        )

        if resp.status_code // 100 != 3:
            raise MobileSSOTGTExpiredError(
                f"CAS 未返回重定向 (HTTP {resp.status_code})，TGT 可能已过期"
            )

        location = resp.headers.get("Location")
        if location is None:
            raise MobileSSOTGTExpiredError("CAS 重定向响应缺少 Location 头")

        if "ticket=" not in location:
            raise MobileSSOTGTExpiredError(
                f"重定向 URL 中未找到 ticket 参数: {location}"
            )

        return location.split("ticket=", 1)[1]
