# payple-hj3415

전자결제시스템. 현재는 네이버페이만 가능하게 설정함
payple_hj3415 앱 - 실제 결제 api로 배포앱
orders - 테스트용 주문앱


## .env 환경변수 구성
```dotenv
PAYPLE_ENV=demo         # demo | live
PAYPLE_CST_ID=test
PAYPLE_CUST_KEY=abcd1234567890
PAYPLE_CLIENT_KEY=test_DF55F29DA654A8CBC0F0A9DD4B556486
PAYPLE_REFERER=http://127.0.0.1:8000    # 로컬 개발 중이면 http://127.0.0.1:8000 로 두고, 정식 테스트계정/운영에선 등록 도메인으로 변경
```

## 프로젝트 urls.py 구성
```python
# myproject/urls.py
from django.urls import path, include
urlpatterns = [
    path("payple/", include(("payple_hj3415.urls", "payple_hj3415"), namespace="payple_hj3415")),
]
```

## 프로젝트 setting.py 구성
```python
INSTALLED_APPS = [
    ...,
    'payple_hj3415',
]

import os
# --- 페이플 설정(테스트 기본값; 운영은 환경변수로 교체) ---
PAYPLE = {
    "ENV": os.getenv("PAYPLE_ENV", "demo"),
    "CST_ID": os.getenv("PAYPLE_CST_ID", "test"),
    "CUST_KEY": os.getenv("PAYPLE_CUST_KEY", "abcd1234567890"),
    "CLIENT_KEY": os.getenv("PAYPLE_CLIENT_KEY", "test_DF55F29DA654A8CBC0F0A9DD4B556486"),
    "REFERER": os.getenv("PAYPLE_REFERER", "http://127.0.0.1:8000"),
}
```

## 다른 앱에서 사용하는 방법(예시)
### 주문모델구성
```python
# orders/models.py
from django.db import models

class Order(models.Model):
    title = models.CharField(max_length=200)               # 예: "테스트 상품"
    amount = models.PositiveIntegerField()                 # KRW(원) 기준 정수 금액
    status = models.CharField(max_length=20, default="PENDING")  # PENDING/PAID/FAILED 등
    created_at = models.DateTimeField(auto_now_add=True)
```

### 뷰에서order 넘기기
```python
# orders/views.py
from django.shortcuts import render, get_object_or_404
from .models import Order

def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # (보안) 본인 주문인지 확인하는 로직 권장
    return render(request, "orders/order_detail.html", {"order": order})
```

### 템플릿에서 사용
```html
{# orders/templates/orders/order_detail.html #}
{% load payple_tags %}
{% url 'orders:done' order.id as done_url %}
{% url 'orders:fail' order.id as fail_url %}

<a class="btn btn-primary"
   href="{% payple_start_url order.id order.amount order.title done_url fail_url %}">
  결제하기
</a>
```

### urls.py 구성
```python
# orders/urls.py
from django.urls import path
from . import views
app_name = "orders"

urlpatterns = [
    path("<int:order_id>/", views.order_detail, name="detail"),
    path("<int:order_id>/done/", views.order_done, name="done"),
    path("<int:order_id>/fail/", views.order_fail, name="fail"),
]
```