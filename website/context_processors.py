from .models import SiteConfig


def site(request):
    return {'site_config': SiteConfig.load()}
