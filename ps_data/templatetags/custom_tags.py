from django import template

register = template.Library()

@register.filter
def to_Y(value):
    return value.replace("Z:\\","Y:\\")