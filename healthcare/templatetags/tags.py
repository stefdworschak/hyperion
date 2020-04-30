from django import template
from django.template.defaultfilters import stringfilter
from datetime import datetime
from dateutil.parser import parse

register = template.Library()

@register.filter
def get(value):
    if value is None:
        return ""
    return value

@register.filter
def format_date(date):
    return parse(date).strftime("%a, %b. %d %y")