from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 4.20.0 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_visma_pay"
    verbose_name = "VismaPay"

    class PretixPluginMeta:
        name = gettext_lazy("Visma Pay")
        author = "Keijo Korte"
        description = gettext_lazy('Accept payments through Visma Pay, a European payment provider supporting '
                                'Finnish Banks and Credit Cards as well as many other payment methods.')
        visible = True
        version = __version__
        category = "PAYMENT"
        picture = "pretix_visma_pay/logo.png"
        compatibility = "pretix>=4.20.0"

    def ready(self):
        from . import signals  # NOQA
