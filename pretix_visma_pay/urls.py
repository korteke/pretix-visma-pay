from django.urls import re_path
from pretix.multidomain import event_url
from django.urls import include, path
from . import views

event_patterns = [
    event_url(r'^visma_pay/callback/(?P<organizer_id>\d+)/(?P<payment_id>\d+)/', 
            views.visma_pay_callback, 
            name="visma_pay_callback"),
]

urlpatterns = [
    re_path(
        r"^visma_pay/callback/(?P<organizer_id>\d+)/(?P<payment_id>\d+)/",
        views.visma_pay_callback,
        name="visma_pay_callback",
    )
]