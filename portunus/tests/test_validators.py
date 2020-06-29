from portunus.validators import DockerNetworkValidator


class Document:
    def __init__(self, string):
        self.text = string


def test_docker_network_validator():
    # TODO have to create a network first based on the validator
    # DockerNetworkValidator().validate(Document('foo'))
    pass
