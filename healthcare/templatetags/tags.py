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
        return parse(date).strftime("%a, %b. %d %Y")
    except:
        return date

@register.filter
def check_future(session_date):
    if parse(session_date).date() <= date.today():
        return True
    else:
        return False

@register.filter
def make_int(strint):
    if isinstance(strint, str):
        return int(strint)
    else:
        return strint