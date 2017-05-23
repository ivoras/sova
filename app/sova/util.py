import bleach

def bleach_htmlfield(html):
    return bleach.clean(html, tags=('b', 'strong', 'i', 'em', 'br', 'p', 'span', 'a', 'ol', 'ul', 'li'),
        attributes={'p': ['style'], 'span': ['style'], 'a': ['href', 'alt', 'title'] })
