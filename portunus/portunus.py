from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from examples import custom_style_2
from PyInquirer import prompt
from PyInquirer import Separator
from PyInquirer import style_from_dict
from PyInquirer import Token

from portunus.validators import IPValidator
from portunus.validators import NumberValidator


class Portunus():

    def __init__(self):
        self.main()

    @staticmethod
    def start(answer):
        return

    @staticmethod
    def cleanup(answer):
        return

    @staticmethod
    def setup(answer):
        faucet_ip = None
        faucet_port = None
        if 'faucet' in answer:
            print('faucet')
        else:
            questions = [
                {
                    'type': 'input',
                    'name': 'faucet_ip',
                    'validate': IPValidator,
                    'message': 'What is the IP of Faucet?',
                },
                {
                    'type': 'input',
                    'name': 'faucet_port',
                    'default': '6653',
                    'message': 'What port Faucet is running on?',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                },
                {
                    'type': 'confirm',
                    'name': 'gauge',
                    'default': True,
                    'message': 'Is Guage being used?',
                },
            ]
            answers = prompt(questions, style=custom_style_2)
            pprint(answers)
        if 'docker' in answer:
            print('docker')
        if 'kvm' in answer:
            print('kvm')
        if 'ovs' in answer:
            print('ovs')
        return

    @staticmethod
    def install(answer):
        print('Installing is not implemented yet, please go install the dependencies yourself at this time.')
        return

    def main(self):
        question = [
            {
                'type': 'checkbox',
                'name': 'intro',
                'message': 'What do you want to do?',
                'choices': [
                    Separator(' ---START--- '),
                    {'name': 'Start Containers', 'checked': True},
                    {'name': 'Start VMs'},
                    Separator(' ---CLEANUP--- '),
                    {'name': 'Cleanup Containers'},
                    {'name': 'Cleanup VMs'},
                    Separator(' ---SETUP--- '),
                    {'name': 'Setup Docker'},
                    {'name': 'Setup KVM'},
                    {'name': 'Setup OVS'},
                    {'name': 'Setup Faucet'},
                    Separator(' ---INSTALL--- '),
                    {'name': 'Install Docker', 'disabled': 'Not implemented yet'},
                    {'name': 'Install KVM', 'disabled': 'Not implemented yet'},
                    {'name': 'Install OVS', 'disabled': 'Not implemented yet'},
                    {'name': 'Install Faucet', 'disabled': 'Not implemented yet'},
                ],
            },
        ]

        answers = prompt(question, style=custom_style_2)
        if 'intro' in answers:
            answers = answers['intro']
            for answer in answers:
                action, thing = answer.lower().split()

                if action == 'start':
                    self.start(thing)
                elif action == 'cleanup':
                    self.cleanup(thing)
                elif action == 'setup':
                    self.setup(thing)
                elif action == 'install':
                    self.install(thing)

        return
