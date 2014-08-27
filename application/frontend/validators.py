# -*- coding: utf-8 -*-

from datetime import date

from pytz import timezone
from wtforms.validators import ValidationError


class ValidateDateNotInFuture(object):
    def __call__(self, form, field):
        if field.data > date.today():
            raise ValidationError('Date cannot be in the future')


def convert_to_bst(dt):
    utc = timezone('UTC').localize(dt)
    bst = timezone('Europe/London').localize(dt)
    return bst + (utc - bst)

