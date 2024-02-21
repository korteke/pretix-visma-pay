from collections import OrderedDict
from django import forms
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _  # NoQA
from pretix.base.signals import (
    logentry_display,
    register_global_settings,
    register_payment_providers,
)


@receiver(register_payment_providers, dispatch_uid="payment_vismapay")
def register_payment_provider(sender, **kwargs):
    from .payment import VismaPayProvider

    return VismaPayProvider


@receiver(signal=logentry_display, dispatch_uid="payment_vismapay_logentry_display")
def logentry_display(sender, logentry, **kwargs):
    if logentry.action_type != "pretix_vismapay.event":
        return

    return _("Vismapay reported an event")


@receiver(register_global_settings, dispatch_uid="visma_pay_global_settings")
def register_global_settings(sender, **kwargs):
    return OrderedDict(
        [
            (
                "payment_visma_pay_api_key",
                forms.CharField(
                    label=_("Visma Pay: API key"),
                    required=False,
                ),
            ),
            (
                "payment_visma_pay_private_key",
                forms.CharField(
                    label=_("Visma Pay: Private key"),
                    required=False,
                ),
            ),
            (
                "payment_visma_pay_test_api_key",
                forms.CharField(
                    label=_("Visma Pay: Test API key"),
                    required=False,
                ),
            ),
            (
                "payment_visma_pay_test_private_key",
                forms.CharField(
                    label=_("Visma Pay: Test private key"),
                    required=False,
                ),
            ),
        ]
    )
