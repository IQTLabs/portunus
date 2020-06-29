import ipaddress
import os

import docker
from PyInquirer import ValidationError
from PyInquirer import Validator


class DockerNetworkValidator(Validator):
    def validate(self, document):
        client = docker.from_env()
        networks = client.networks.list(
            document.text, filters={'driver': 'ovs'})
        if len(networks) != 1 or document.text == '':
            raise ValidationError(
                message='Please enter the name of a Docker network with the OVS driver',
                cursor_position=len(document.text))  # pragma: no cover


class IPValidator(Validator):
    def validate(self, document):
        try:
            ipaddress.ip_address(document.text)
        except ValueError:  # pragma: no cover
            raise ValidationError(
                message='Please enter an IP address',
                cursor_position=len(document.text))  # pragma: no cover


class ImageValidator(Validator):
    def validate(self, document):
        if not os.path.isfile(document.text):
            raise ValidationError(
                message='Please enter a path to an image that exists',
                cursor_position=len(document.text))  # pragma: no cover
        if not document.text.endswith('.img') and not document.text.endswith('.qcow2'):
            raise ValidationError(
                message='Image must be either a .img or a .qcow2 image',
                cursor_position=len(document.text))  # pragma: no cover


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:  # pragma: no cover
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # pragma: no cover
        if int(document.text) < 0:
            raise ValidationError(
                message='Please enter a number 0 or higher',
                cursor_position=len(document.text))  # pragma: no cover


class PortValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:  # pragma: no cover
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # pragma: no cover
        if int(document.text) < 1 or int(document.text) > 65535:
            raise ValidationError(
                message='Please enter a number between 1-65535',
                cursor_position=len(document.text))  # pragma: no cover
