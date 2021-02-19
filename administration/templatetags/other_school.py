from django import template

register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter('startswithrettext')
def startswithrettext(text, starts):
    if isinstance(text, str):
        return starts if text.startswith(starts) else False
    return False

@register.filter('removeother')
def removeother(text):
    if isinstance(text, str):
        return text.replace("Other - ", "")
    return text
