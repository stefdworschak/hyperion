from django import template
from django.template.defaultfilters import stringfilter
from datetime import datetime, timedelta, date
from dateutil.parser import parse

register = template.Library()

@register.filter
def get(value):
    if value is None:
        return ""
    return value

@register.filter
def format_date(date):
    try:
        return parse(date).strftime("%a, %b. %d %y")
    except:
        return date
