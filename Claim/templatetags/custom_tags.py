from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter
def is_manager(user):
    return user.groups.filter(name='Manager').exists()

@register.filter
def is_Accounts(user):
    return user.groups.filter(name='Accounts').exists()