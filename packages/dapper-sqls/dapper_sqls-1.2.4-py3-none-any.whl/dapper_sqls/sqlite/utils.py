# coding: utf-8
import re

def is_valid_name(name, max_length=255):
    return bool(name and len(name) <= max_length and re.match(r'^[\w\s]+$', name))

def get_value(value):
        return getattr(value, 'value', value)

