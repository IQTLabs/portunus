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
                cursor_position=len(document.text))  # Move cursor to end


class IPValidator(Validator):
    def validate(self, document):
        try:
            ipaddress.ip_address(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter an IP address',
                cursor_position=len(document.text))  # Move cursor to end


class KVMImageValidator(Validator):
    def validate(self, document):
        if not os.path.isfile(document.text):
            raise ValidationError(
                message='Please enter a path to a KVM image that exists',
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
