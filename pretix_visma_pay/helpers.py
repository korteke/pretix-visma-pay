import logging
from pretix.base.settings import GlobalSettingsObject

logger = logging.getLogger(__name__)


def get_credentials(event):
    gs = GlobalSettingsObject()
    try:
        api_key_setting = (
            "payment_visma_pay_test_api_key"
            if event.testmode
            else "payment_visma_pay_api_key"
        )
        private_key_setting = (
            "payment_visma_pay_test_private_key"
            if event.testmode
            else "payment_visma_pay_private_key"
        )
        return {
            "api_key": gs.settings.get(api_key_setting),
            "private_key": gs.settings.get(private_key_setting),
        }
    except Exception as e:

        logger.exception("Unable to fetch credentials from settings.")
        return False
