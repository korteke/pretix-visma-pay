import logging
from collections import OrderedDict
from decimal import Decimal
from django.http import HttpRequest
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.forms import SecretKeySettingsField
from pretix.base.models import Event, Order
from pretix.base.payment import BasePaymentProvider, PaymentException
from pretix.base.settings import SettingsSandbox
from secrets import token_urlsafe

from .helpers import get_credentials
from .visma_pay import VismaPayClient

logger = logging.getLogger("pretix_visma_pay")


class VismapaySettingsHolder(BasePaymentProvider):
    identifier = "vismapay_settings"
    verbose_name = _("Visma Pay")
    is_enabled = False
    is_meta = True
    payment_methods_settingsholder = []

    def __init__(self, event: Event):
        super().__init__(event)
        self.settings = SettingsSandbox("payment", self.identifier.split("_")[0], event)

    @property
    def settings_form_fields(self):
        fields = [
            (
                "privatekey",
                SecretKeySettingsField(
                    label=_("Private Key"),
                    help_text=_(
                        "Your merchant account's private key, "
                        "to be found in your payment provider's settings: "
                        "'Merchant' > scroll down to 'Merchant-Settings' and copy the key."
                    ),
                ),
            ),
            (
                "apikey",
                SecretKeySettingsField(
                    label=_("API Key"),
                    help_text=_(
                        "Your API key for an API user, "
                        "to be found in your payment provider's settings: 'User' where you select the 'System user' "
                        "that is configured to have rights to access only '/payments' functionality and copy it's key. "
                        "If you have no such user, please create one with the above mentioned permissions first."
                    ),
                ),
            ),
        ]
        d = OrderedDict(
            fields
            + self.payment_methods_settingsholder
            + list(super().settings_form_fields.items())
        )

        d.move_to_end("_enabled", last=False)
        return d


class VismaPayProvider(BasePaymentProvider):
    def __init__(self, event):
        super().__init__(event)

        credentials = get_credentials(event)
        self.client = VismaPayClient(
            credentials.get("api_key"), credentials.get("private_key")
        )

    def checkout_confirm_render(self, request):
        return _("You will be redirected to Visma Pay to complete the payment")

    def execute_payment(self, request, payment):
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
        token = self.client.get_token(
            order_number=order_number,
            amount=int(payment.amount * 100),
            email=payment.order.email,
            callback_url=callback_url,
        )

        return self.client.payment_url(token)

    @property
    def identifier(self):
        return "visma_pay"

    def payment_is_valid_session(self, request):
        return True

    def payment_form_render(
        self, request: HttpRequest, total: Decimal, order: Order = None
    ) -> str:
        template = get_template("pretix_visma_pay/payment_form.html")
        return template.render()

    @property
    def public_name(self):
        return "{} – {}".format(_("Bank and credit card payments"), self.verbose_name)

    @property
    def test_mode_message(self):
        return _(
            "Payment will be simulated while the shop is in test mode. No money will be transferred. Read more at: %(url)s"
        ) % {"url": "https://payform.bambora.com/docs/web_payments/?page=testing"}

    @property
    def verbose_name(self):
        return "Visma Pay"
