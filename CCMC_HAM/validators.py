"""输入校验工具"""
import re


def is_valid_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email or ''))


def is_valid_phone(phone):
    return bool(re.match(r'^[0-9 +()-]{6,25}$', phone or '')) if phone else True

