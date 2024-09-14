import hmac
import logging
import requests
from django.utils.translation import gettext_lazy as _
from pretix.base.payment import PaymentException

logger = logging.getLogger("pretix_visma_pay")


class VismaPayClient:
    API_VERSION = "w3.1"
    BASE_URL = "https://www.vismapay.com/pbwapi"

    def __init__(self, api_key, private_key):
        self.api_key = api_key
        self.private_key = private_key

    def get_payment_token(
        self, order_number=None, amount=None, email=None, callback_url=None
    ):
        authcode_input = "|".join([self.api_key, order_number])
        logging.debug(
            "order_number: [%s] - email: [%s] - authcode: [%s]",
            order_number,
            email,
            authcode_input,
        )
        payload = {
            "version": self.API_VERSION,
            "api_key": self.api_key,
            "order_number": order_number,
            "amount": amount,
            "currency": "EUR",
            "email": email,
            "payment_method": {
                "type": "e-payment",
                "return_url": callback_url,
                "notify_url": callback_url,
                "lang": "en",
            },
            "authcode": self.generate_authcode(authcode_input),
        }

        try:
            r = requests.post(f"{self.BASE_URL}/auth_payment", json=payload)
            resp = r.json()
            logger.debug("Response from Visma %s \n" % resp)
        except Exception as e:
            logger.exception("VismaPay Payment error: %s" % e)
            raise PaymentException(
                _("We had trouble communicating with the payment provider.")
            )

        if resp.get("result") != 0:
            raise Exception(
                f"Token request failed with code {resp.get('result')}: {resp.get('errors')} - {resp.get('url')}"
            )

        return resp.get("token")

    def get_payment_methods(self):
        payload = {
            "version": "2",
            "api_key": self.api_key,
            "currency": "EUR",
            "authcode": self.generate_authcode(self.api_key),
        }

        r = requests.post(
            "{}/merchant_payment_methods".format(self.BASE_URL), json=payload
        )

        resp = r.json()
        logger.debug("Response from VismaPay payment methods %s \n" % resp)

        if resp.get("result") != 0:
            raise Exception(
                f"Payment methods request failed with code {resp.get('result')}: {resp.get('errors')} - {resp.get('url')}"
            )

        return resp

    def payment_url(self, token):
        return "{}/token/{}".format(self.BASE_URL, token)

    def validate_callback_request(self, r):
        try:
            return_code = r.GET.get("RETURN_CODE")
            order_number = r.GET.get("ORDER_NUMBER")
            settled = r.GET.get("SETTLED")
            incident_id = r.GET.get("INCIDENT_ID")
            authcode = r.GET.get("AUTHCODE")

            authcode_parts = [return_code, order_number]
            if settled is not None:
                authcode_parts.append(settled)

            if incident_id is not None:
                authcode_parts.append(incident_id)

            authcode_input = "|".join(authcode_parts)
            if authcode != self.generate_authcode(authcode_input):
                return False

            return True
        except Exception as e:
            logger.exception("Error validating callback request")
            return False

    def generate_authcode(self, input):
        """
        MAC code for the payment. It is calculated using HMAC-SHA256. HMAC implementations exist for most popular programming languages.
        Sub-merchant private key is used as the secret key and the message is calculated from the values of the following fields:
            * api_key
            * order_number
        Fields are joined with '|' character and they are appended in the specified order. The authcode must always be in UPPERCASE.
        """
        return (
            hmac.new(
                self.private_key.encode("utf8"),
                input.encode("utf8"),
                digestmod="sha256",
            )
            .hexdigest()
            .upper()
        )
