import logging
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_scopes import scope
from pretix.base.models import Order, OrderPayment, Organizer
from pretix.base.payment import PaymentException
from pretix.multidomain.urlreverse import eventreverse

from .helpers import get_credentials
from .visma_pay import VismaPayClient

logger = logging.getLogger(__name__)


def visma_pay_callback(request, organizer_id=None, payment_id=None):
    return_code = request.GET.get("RETURN_CODE")
    settled = request.GET.get("SETTLED")
    order_number = request.GET.get("ORDER_NUMBER")
    order_code = order_number.split("_")[0]
    logger.debug(
        "Redirect request: ReturnCode: [%s] Settled: [%s] OrderNumber: [%s] OrderCode: [%s]",
        return_code,
        settled,
        order_number,
        order_code,
    )

    try:
        organizer = Organizer.objects.get(id=organizer_id)
        with scope(organizer=organizer):
            payment = OrderPayment.objects.get(id=payment_id)
            order = payment.order
            event = order.event

            credentials = get_credentials(event)
            client = VismaPayClient(
                credentials.get("api_key"), credentials.get("private_key")
            )
            if not client.validate_callback_request(request):
                raise PaymentException("Invalid request")

            if payment.order.code != order_code:
                raise PaymentException("Invalid request")

            if return_code == "0" and settled == "1":
                payment.confirm()
                order.refresh_from_db()

            logger.debug("order secret: %s", order.secret)
            redirect_url = eventreverse(
                event,
                "presale:event.order",
                kwargs={"order": order.code, "secret": order.secret},
            ) + ("?paid=yes" if order.status == Order.STATUS_PAID else "")

            return redirect(redirect_url)
    except Order.DoesNotExist:
        raise Exception("Order does not exist!")
