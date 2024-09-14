import logging
from collections import OrderedDict
from decimal import Decimal
from django.http import HttpRequest
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from pretix.base.models import Order, OrderPayment
from django import forms
from pretix.base.models import Event, Order
from pretix.base.payment import BasePaymentProvider, PaymentException
from pretix.base.settings import SettingsSandbox
from secrets import token_urlsafe

from .helpers import get_credentials
from .visma_pay import VismaPayClient

logger = logging.getLogger(__name__)


class VismaPayProvider(BasePaymentProvider):
    def __init__(self, event):
        super().__init__(event)

        credentials = get_credentials(event)
        self.client = VismaPayClient(
            credentials.get("api_key"), credentials.get("private_key")
        )

    def checkout_confirm_render(self, request):
        return _(
            "After you submitted your order, we will redirect you to Visma Pay to complete your payment. You will then be redirected back here to get your tickets."
        )

    def execute_payment(self, request: HttpRequest, payment: OrderPayment):
        callback_url = request.build_absolute_uri(
            reverse(
                "plugins:pretix_visma_pay:visma_pay_callback",
                kwargs={
                    "payment_id": payment.id,
                    "organizer_id": payment.order.event.organizer.id,
                },
            )
        )

        order_number = "{}_{}".format(payment.order.code, token_urlsafe(16))
        try:
            token = self.client.get_payment_token(
                order_number=order_number,
                amount=int(
                    payment.amount * 100
                ),  # Amount is in fractional monetary units e.g. 1€ = 100.
                email=payment.order.email,
                callback_url=callback_url,
            )
            logger.debug("VismaPay token: %s", token)
        except Exception as e:
            logger.exception("VismaPay Payment error: %s" % e)
            raise PaymentException(
                _("We had trouble communicating with the payment provider.")
            )

        return self.client.payment_url(token)

    @property
    def identifier(self):
        return "visma_pay"

    def payment_control_render(self, request: HttpRequest, payment: OrderPayment):
        template = get_template("pretix_visma_pay/control.html")
        ctx = {
            "request": request,
            "event": self.event,
            "settings": self.settings,
            "payment_info": payment.info_data,
            "order": payment.order,
            "provname": self.verbose_name,
        }
        return template.render(ctx)

    def payment_is_valid_session(self, request):
        return True

    def payment_form_render(
        self, request: HttpRequest, total: Decimal, order: Order = None
    ) -> str:
        template = get_template("pretix_visma_pay/payment_form.html")
        return template.render()

    @property
    def public_name(self) -> str:
        return "{} – {}".format(
            _("Finnish online bank and credit card payments"), self.verbose_name
        )

    @cached_property
    def test_mode_message(self) -> str:
        return _(
            "In test mode, only test cards will work. Visa: 4012888888881881. MasterCard: 5244024870672677"
        )

    @property
    def verbose_name(self) -> str:
        return "Visma Pay"
