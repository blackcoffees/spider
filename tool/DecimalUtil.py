# -*- coding: utf-8 -*-
from decimal import Decimal

# 精度控制  value:值，precision：精度
import decimal


def decimal_round(value, precision=2):
    # prestr = Decimal(1.0 / (10**int(precision)))
    value = Decimal(str(value))
    prestr = ''
    while (True):
        if precision - 1 > len(prestr):
            prestr = prestr + '0'
        else:
            prestr = prestr + '1'
            break
    prestr = '0.' + prestr
    return value.quantize(Decimal(prestr), rounding=decimal.ROUND_HALF_EVEN)


def decimal_sum(obj1, obj2, precision=2):
    obj1 = Decimal(str(obj1))
    obj2 = Decimal(str(obj2))
    result = decimal_round(obj1 + obj2, precision)
    return result


def decimal_sub(obj1, obj2, precision=2):
    obj1 = Decimal(str(obj1))
    obj2 = Decimal(str(obj2))
    result = decimal_round(obj1 - obj2, precision)
    return result


def decimal_div(obj1, obj2, precision=2):
    obj1 = Decimal(str(obj1))
    obj2 = Decimal(str(obj2))
    result = decimal_round(obj1 / obj2, precision)
    return result


def default_decimal(obj):
    if isinstance(obj, Decimal):
        return str(obj)