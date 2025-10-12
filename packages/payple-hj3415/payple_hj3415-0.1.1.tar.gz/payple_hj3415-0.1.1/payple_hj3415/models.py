# payple_hj3415/models.py
from django.db import models

class Payment(models.Model):
    oid = models.CharField(max_length=64, db_index=True)  # 상점 주문번호
    goods = models.CharField(max_length=200)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="PENDING")  # PENDING/AUTHED/CONFIRMED/FAILED/CANCELED
    reqkey = models.CharField(max_length=200, blank=True)
    auth_key = models.TextField(blank=True)
    trade_num = models.CharField(max_length=100, blank=True)
    auth_no = models.CharField(max_length=50, blank=True)
    receipt_url = models.URLField(blank=True)
    success_url = models.URLField(blank=True)
    fail_url = models.URLField(blank=True)
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "결제 아이템"
        verbose_name_plural = "결제 아이템"