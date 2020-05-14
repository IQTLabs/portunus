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
        # TODO
        return {}

    @staticmethod
    def cleanup(answer):
        # TODO
        return {}

    @staticmethod
    def setup(answer):
        info = {}
        if 'faucet' in answer:
            print('setting up faucet...')
            # TODO
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
                    'message': 'What port is Faucet running on?',
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
            info.update(answers)
            if answers['gauge']:
                questions = [
                    {
                        'type': 'input',
                        'name': 'gauge_ip',
                        'default': answers['faucet_ip'],
                        'validate': IPValidator,
                        'message': 'What is the IP of Gauge?',
                    },
                    {
                        'type': 'input',
                        'name': 'gauge_port',
                        'default': '6654',
                        'message': 'What port is Gauge running on?',
                        'validate': NumberValidator,
                        'filter': lambda val: int(val)
                    },
                ]
                answers = prompt(questions, style=custom_style_2)
                info.update(answers)
        if 'docker' in answer:
            print('docker')
            # TODO
        if 'kvm' in answer:
            print('kvm')
            # TODO
        if 'ovs' in answer:
            print('ovs')
            # TODO

        return info

    @staticmethod
    def install(answer):
        print('Installing is not implemented yet, please go install the dependencies yourself at this time.')
        return {}

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
        info_dict = {}
        if 'intro' in answers:
            answers = answers['intro']
            for answer in answers:
                action, thing = answer.lower().split()

                if action == 'start':
                    info_dict.update(self.start(thing))
                elif action == 'cleanup':
                    info_dict.update(self.cleanup(thing))
                elif action == 'setup':
                    info_dict.update(self.setup(thing))
                elif action == 'install':
                    info_dict.update(self.install(thing))
        print(info_dict)
        # TODO use info_dict to perform necessary actions

        return
