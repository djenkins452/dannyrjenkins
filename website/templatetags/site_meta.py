from django import template

register = template.Library()

DEFAULT_OWNER = 'Danny R. Jenkins'


@register.simple_tag(takes_context=True)
def page_title(context, title):
    """Browser title for a page with an optional admin-entered SEO title.

    An SEO title that already names the site owner is used verbatim, so no
    name or section suffix is added twice. Anything else gets the owner name
    appended once: "<title> — Danny R. Jenkins".
    """
    config = context.get('site_config')
    owner = (getattr(config, 'brand_wordmark', '') or DEFAULT_OWNER).strip()
    title = (title or '').strip()
    if not title:
        return owner
    if owner.lower() in title.lower():
        return title
    return f'{title} — {owner}'
