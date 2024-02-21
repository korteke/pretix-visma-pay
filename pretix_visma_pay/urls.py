# from django.conf.urls import url
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^visma_pay/callback/(?P<organizer_id>\d+)/(?P<payment_id>\d+)/",
        views.visma_pay_callback,
        name="visma_pay_callback",
    )
]
