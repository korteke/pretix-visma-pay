from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_visma_pay"
    verbose_name = "VismaPay"

    class PretixPluginMeta:
        name = gettext_lazy("VismaPay")
        author = "Keijo Korte"
        description = gettext_lazy("Visma Pay payment plugin")
        visible = True
        version = __version__
        category = "PAYMENT"
        picture = "pretix_visma_pay/logo.png"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA
