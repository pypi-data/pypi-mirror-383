# payple_hj3415/urls.py
from django.urls import path, re_path
from . import views

app_name = 'payple_hj3415'

urlpatterns = [
    path("start/", views.start, name="start"),
    re_path(r"^pay/?$", views.pay_page, name="payple_pay_page"),            # 결제 버튼/JS
    re_path(r"^result/?$", views.payple_result, name="payple_result"),      # PCD_RST_URL(서버 POST 수신)
    re_path(r"^confirm/?$", views.payple_confirm, name="payple_confirm"),   # 승인 API 호출
    re_path(r"^webhook/?$", views.payple_webhook, name="payple_webhook"),   # 선택(비동기 보강)
]
