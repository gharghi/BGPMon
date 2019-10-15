from netaddr import IPAddress, IPNetwork
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.ipv6 import is_valid_ipv6_address


def validate_ipv46_address(value):
    try:
        validate_ipv4_address(value)
    except ValidationError:
        try:
            validate_ipv6_address(value)
        except ValidationError:
            raise ValidationError(_('Enter a valid IPv4 or IPv6 address.'), code='invalid')


def validate_ipv46_network(value):
    try:
        if validate_ipv4_network(value):
            return value
    except ValidationError:
        try:
            validate_ipv6_network(value)
        except ValidationError:
            raise ValidationError(_('Enter a valid IPv4 or IPv6 network.'), code='invalid')
            return False


def validate_ipv6_address(value):
    if not is_valid_ipv6_address(value):
        raise ValidationError(_('Enter a valid IPv6 address.'), code='invalid')


def validate_ipv4_address(value):
    try:
        if IPAddress(value):
            return value
    except ValueError:
        raise ValidationError(_('Enter a valid IPv4 address.'), code='invalid')


def validate_ipv4_network(value):
    try:
        IPNetwork(value)
    except ValueError:
        raise ValidationError(_('Enter a valid IPv4 network.'), code='invalid')


def validate_ipv6_network(value):
    try:
        IPNetwork(value)
    except ValueError:
        raise ValidationError(_('Enter a valid IPv6 network.'), code='invalid')
