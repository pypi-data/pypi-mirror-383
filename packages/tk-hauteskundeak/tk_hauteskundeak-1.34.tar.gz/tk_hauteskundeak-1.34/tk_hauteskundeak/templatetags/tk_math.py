import re
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def tokiak_in_cols(tokiak):
    cols = {}
    for tokia in tokiak:
        if tokia.order_col not in cols.keys():
            cols[tokia.order_col] = []
        cols[tokia.order_col].append(tokia)

    tor = []
    for k,v in cols.items():
        h2 = {}
        h2['col'] = k
        h2['tokiak'] = v
        tor.append(h2)
    return tor

@register.filter
def divide(value, arg):
    try:
        return int(value)*100.0 / int(arg)
    except (ValueError, ZeroDivisionError):
        return None


@register.filter
def get_botoak(item, i):
    return getattr(item, 'botoak_{}'.format(i))        

@register.filter
def get_ehunekoa(item, i):
    v = getattr(item, 'ehunekoa_{}'.format(i))            
    if v:
        return '%{}'.format(round(v,2))
    else:
        return ''

@register.filter
def get_jarlekuak(item, i):
    v = getattr(item, 'jarlekuak_{}'.format(i))            
    if v:
        return '({})'.format(v)
    else:
        return ''


@register.filter
def get_abstentzioa(errolda, boto_emaileak):
    return errolda-boto_emaileak

@register.filter
def divide_abstentzioa(errolda, boto_emaileak):
    abstentzioa = errolda-boto_emaileak
    try:
        return int(abstentzioa)*100.0 / int(errolda)
    except (ValueError, ZeroDivisionError):
        return None
@register.filter
def get_diferentzia(item):
    botoak1 = getattr(item, 'botoak_1')        
    botoak2 = getattr(item, 'botoak_0')   
    if botoak1 and botoak2:
        dif = botoak1 - botoak2
        if dif < 0:
            cl = 'text-danger'     
        else:
            cl = ''

        difehunekoa = round(dif*100.0/botoak2,2)
        difehunekoa = '(%{})'.format(difehunekoa)
        return '<span class="{}">{} <small>{}</small></span>'.format(cl, dif, difehunekoa)
    else:
        return  '-'
    
