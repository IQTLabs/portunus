import os
from pathlib import Path

from portunus.validators import ImageValidator
from portunus.validators import IPValidator
from portunus.validators import NumberValidator
from portunus.validators import PortValidator


class Document:
    def __init__(self, string):
        self.text = string


def test_ip_validator():
    IPValidator().validate(Document('192.168.1.1'))


def test_image_validator():
    Path('test.img').touch()
    ImageValidator().validate(Document('test.img'))
    os.remove('test.img')


def test_number_validator():
    NumberValidator().validate(Document('1'))


def test_port_validator():
    PortValidator().validate(Document('1'))
