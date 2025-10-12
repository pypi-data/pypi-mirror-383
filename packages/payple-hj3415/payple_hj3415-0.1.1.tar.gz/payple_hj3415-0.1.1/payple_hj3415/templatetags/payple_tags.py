# payple_hj3415/templatetags/payple_tags.py
from django import template
from .. import services

register = template.Library()

@register.simple_tag(takes_context=True)
def payple_start_url(context, oid, amount, goods, success_url, fail_url):
    token = services.make_start_token(oid, amount, goods, success_url, fail_url)
    return services.build_start_url(context["request"], token)