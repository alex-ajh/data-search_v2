from django import template

register = template.Library()

@register.filter
def to_Y(value):
    return value.replace("Z:\\","Y:\\")

@register.filter
def replace_slash(value):
    return value.replace("\\","/")
