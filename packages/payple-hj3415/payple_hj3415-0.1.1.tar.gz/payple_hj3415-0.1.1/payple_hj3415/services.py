# payple_hj3415/services.py
from django.core import signing
from django.urls import reverse

_SALT = "payple_hj3415.start"

def make_start_token(oid: str, amount: int, goods: str, success_url: str, fail_url: str) -> str:
    payload = {"oid": oid, "amount": int(amount), "goods": goods,
               "success_url": success_url, "fail_url": fail_url}
    return signing.dumps(payload, salt=_SALT)

def parse_start_token(token: str, max_age=600) -> dict:
    # 10분 유효(인증→승인 타임리밋과도 잘 맞음)
    return signing.loads(token, salt=_SALT, max_age=max_age)

def build_start_url(request, token: str) -> str:
    return request.build_absolute_uri(reverse("payple_hj3415:start") + f"?t={token}")