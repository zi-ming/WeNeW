from django import template

register = template.Library()

@register.filter
def urlDecode(url):
    return url.replace("(-)__(-)","&")