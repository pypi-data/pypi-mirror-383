# payple_hj3415/views.py
import uuid, requests, json, logging
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from .models import Payment
import secrets
from . import services

logger = logging.getLogger(__name__)

def start(request):
    token = request.GET.get("t")
    if not token:
        return HttpResponseBadRequest("missing token")
    try:
        payload = services.parse_start_token(token)
    except Exception:
        return HttpResponseBadRequest("invalid/expired token")

    base_oid = str(payload["oid"])  # 예: order_id
    unique_oid = f"{base_oid}-{timezone.now():%Y%m%d%H%M%S}-{secrets.token_hex(3)}"

    # (보안) 실제 주문 DB 금액과 payload['amount']가 같은지 검증 권장
    pay = Payment.objects.create(
        oid=unique_oid, goods=payload["goods"], amount=payload["amount"],
        success_url=payload["success_url"], fail_url=payload["fail_url"],
        status="PENDING",
    )

    # 결과 리다이렉트를 위한 세션 폴백값 저장
    request.session["PAYPLE_OID"] = str(pay.oid)
    request.session["PAYPLE_SUCCESS_URL"] = pay.success_url
    request.session["PAYPLE_FAIL_URL"] = pay.fail_url

    rst_url = request.build_absolute_uri(reverse("payple_hj3415:payple_result"))
    # print(settings.PAYPLE['ENV'])
    return render(request, "payple_hj3415/payple_pay.html", {
        'payple_env': settings.PAYPLE['ENV'],
        "client_key": settings.PAYPLE["CLIENT_KEY"],
        "goods": pay.goods,
        "amount": pay.amount,
        "rst_url": rst_url,  # 절대 URL
        "oid": pay.oid,
    })

def pay_page(request):
    # 주문번호(예시) - 중복 불가. 실제로는 Order 모델과 묶어 저장을 권장
    request.session["pay_oid"] = f"order-{uuid.uuid4()}"
    return render(request, "payple_hj3415/payple_pay.html", {
        'payple_env': settings.PAYPLE['ENV'],
        "client_key": settings.PAYPLE["CLIENT_KEY"]
    })

@csrf_exempt  # 페이플이 서버로 POST하는 엔드포인트만 CSRF 예외
def payple_result(request):
    """
    [2단계] 인증결과 수신(PCD_RST_URL)
    응답에는 PCD_AUTH_KEY, PCD_PAY_REQKEY, PCD_PAY_COFURL 등이 포함됨.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    # payload 파싱: x-www-form-urlencoded 우선, 없으면 JSON도 허용
    data = None
    try:
        if request.POST:
            data = request.POST
        else:
            # JSON 시도
            body = (request.body or b"").decode("utf-8")
            data = json.loads(body) if body else {}
    except Exception as e:
        logger.warning("payple_result parse error: %s", e)
        data = {}

    print("PAYPLE_RESULT_POST:", {
        "PCD_PAY_RST": data.get("PCD_PAY_RST"),
        "PCD_PAY_CODE": data.get("PCD_PAY_CODE"),
        "PCD_PAY_MSG": data.get("PCD_PAY_MSG"),
        "PCD_AUTH_KEY": data.get("PCD_AUTH_KEY"),
        "PCD_PAY_REQKEY": data.get("PCD_PAY_REQKEY"),
    })

    # 키 추출 (대소문자/포맷 유연화)
    pay_rst  = (data.get("PCD_PAY_RST") or data.get("pcd_pay_rst") or "").lower()
    auth_key = data.get("PCD_AUTH_KEY") or data.get("pcd_auth_key")
    req_key  = data.get("PCD_PAY_REQKEY") or data.get("pcd_pay_reqkey")
    cof_url  = data.get("PCD_PAY_COFURL") or data.get("pcd_pay_cofurl")
    oid      = data.get("PCD_PAY_OID") or data.get("pcd_pay_oid") or request.session.get("PAYPLE_OID")
    err_code = data.get("PCD_PAY_CODE") or data.get("pcd_pay_code")
    err_msg  = data.get("PCD_PAY_MSG") or data.get("pcd_pay_msg")

    # 실패 처리: close/error 등 모든 비-성공 케이스는 즉시 실패 URL로
    if pay_rst != "success" or not all([auth_key, req_key, cof_url]):
        logger.info("payple_result fail: rst=%s code=%s msg=%s", pay_rst, err_code, err_msg)
        # 디버깅용 세션 기록
        request.session["PAYPLE_LAST_RESULT"] = {
            "rst": pay_rst, "code": err_code, "msg": err_msg, "oid": oid,
        }
        # 세션/DB 폴백으로 실패 URL 리다이렉트
        fail_url = request.session.get("PAYPLE_FAIL_URL")
        if not fail_url and oid:
            pay = Payment.objects.filter(oid=oid).only("fail_url").first()
            if pay:
                fail_url = pay.fail_url
        if fail_url:
            return redirect(fail_url)
        return HttpResponse("인증 실패", status=400)

    # 성공: 승인 단계에서 사용할 값 보관 후 승인 단계로 이동
    request.session["PAYPLE_AUTH_KEY"] = auth_key
    request.session["PAYPLE_PAY_REQKEY"] = req_key
    request.session["PAYPLE_COF_URL"] = cof_url
    # 참고용
    if oid:
        request.session["PAYPLE_OID"] = str(oid)

    return redirect("payple_hj3415:payple_confirm")

def payple_confirm(request):
    """
    [3단계] 승인 API 호출(실결제)
    - Referer는 페이플에 등록된 도메인과 같아야 함
    - 기본적으로 result 단계에서 받은 PCD_PAY_COFURL로 호출 (없으면 폴백)
    - 인증→승인은 10분 내 완료
    """
    # 1) 세션에서 값 로드 (+ 폴백)
    cof_url  = request.session.get("PAYPLE_COF_URL") \
               or (f"{settings.PAYPLE_API_BASE}/api/v1/payments/cards/approval/confirm")
    auth_key = request.session.get("PAYPLE_AUTH_KEY")
    req_key  = request.session.get("PAYPLE_PAY_REQKEY")

    if not all([auth_key, req_key]):
        return HttpResponse("인증/승인 정보 없음", status=400)

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Referer": settings.PAYPLE["REFERER"],  # 등록 도메인과 정확히 일치
    }
    body = {
        "PCD_CST_ID": settings.PAYPLE["CST_ID"],
        "PCD_CUST_KEY": settings.PAYPLE["CUST_KEY"],  # 비노출 주의
        "PCD_AUTH_KEY": auth_key,
        "PCD_PAY_REQKEY": req_key,
    }

    # 2) 승인 호출(예외 대비)
    try:
        resp = requests.post(cof_url, headers=headers, json=body, timeout=10)
        data = resp.json() if resp.content else {}
    except requests.RequestException as e:
        return JsonResponse({"ok": False, "error": "network", "detail": str(e)}, status=502)
    except ValueError:
        return JsonResponse({"ok": False, "error": "bad_json", "raw": resp.text[:500]}, status=502)

    ok = resp.ok and data.get("PCD_PAY_RST") == "success"
    oid = data.get("PCD_PAY_OID")  # 주문번호(시작 단계에서 지정한 값이 돌아옴)

    # 3) 멱등성 있게 DB 반영
    pay = None
    with transaction.atomic():
        pay = Payment.objects.select_for_update().filter(oid=oid).first()
        if pay:
            if ok and pay.status != "CONFIRMED":
                pay.status = "CONFIRMED"
                pay.reqkey = req_key
                pay.auth_key = auth_key
                pay.trade_num = data.get("PCD_PAY_CARDTRADENUM", "")
                pay.auth_no = data.get("PCD_PAY_CARDAUTHNO", "")
                pay.receipt_url = data.get("PCD_PAY_CARDRECEIPT", "")
                pay.approved_at = timezone.now()
                pay.save()
            elif not ok and pay.status not in ("CONFIRMED", "CANCELED"):
                pay.status = "FAILED"
                pay.save()

    # 4) 호스트 앱으로 리다이렉트(있으면)
    if pay:
        if ok and pay.success_url:
            return redirect(pay.success_url)
        if (not ok) and pay.fail_url:
            return redirect(pay.fail_url)

    # 5) 기본 JSON 응답
    return JsonResponse({"ok": ok, "result": data}, status=200 if ok else 400)

@csrf_exempt
def payple_webhook(request):
    """
    선택: 웹훅으로 결제완료/취소 등을 비동기 수신해 중복/지연 대응
    """
    if request.method == "POST":
        # 필요 시 서명/화이트리스트 검증 로직 추가
        return HttpResponse("OK")
    return HttpResponse(status=405)