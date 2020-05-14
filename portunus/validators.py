import ipaddress

from PyInquirer import ValidationError
from PyInquirer import Validator


class IPValidator(Validator):
    def validate(self, document):
        try:
            ipaddress.ip_address(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter an IP address',
                cursor_position=len(document.text))  # Move cursor to end


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end
        if int(document.text) < 1 or int(document.text) > 65535:
            raise ValidationError(
                message='Please enter a number between 1-65535',
                cursor_position=len(document.text))  # Move cursor to end
