from __future__ import print_function
from __future__ import unicode_literals

import subprocess
import sys
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
    def execute_command(command, message):
        print(message)
        try:
            process = subprocess.Popen(command,
                                       stdout=subprocess.PIPE,
                                       universal_newlines=True)
        except FileNotFoundError:
            print(f'Command "{" ".join(command)}" not found!')
            return 1

        return_code = None
        while True:
            output = process.stdout.readline()
            print(output.strip())
            return_code = process.poll()
            if return_code is not None:
                for output in process.stdout.readlines():
                    print(output.strip())
                break
        return return_code

    @staticmethod
    def start_info(selections):
        # TODO
        return {}

    @staticmethod
    def cleanup_info(selections):
        # TODO
        return {}

    def setup_info(self, selections):
        info = {}
        if 'faucet' in selections:
            commands = [
                # TODO put in real commands
                (['ping', '-c 4', 'python.org'], 'setting up Faucet...'),
            ]
            for command in commands:
                if self.execute_command(command[0], command[1]) != 0:
                    sys.exit(1)
        else:
            faucet_questions = [
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
                    'message': 'Is Gauge being used?',
                },
            ]
            answers = prompt(faucet_questions, style=custom_style_2)
            info.update(answers)
            if 'gauge' in answers and answers['gauge']:
                gauge_questions = [
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
                answers = prompt(gauge_questions, style=custom_style_2)
                info.update(answers)
        if 'docker' in selections:
            print('setting up docker...')
            # TODO
        if 'kvm' in selections:
            print('kvm')
            # TODO
        if 'ovs' in selections:
            print('ovs')
            # TODO

        return info

    @staticmethod
    def install_info(selections):
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
        action_dict = {
            'start': self.start_info,
            'cleanup': self.cleanup_info,
            'setup': self.setup_info,
            'install': self.install_info
        }
        if 'intro' in answers:
            answers = answers['intro']
            actions = {}
            for answer in answers:
                action, selection = answer.lower().split()
                if action not in actions:
                    actions[action] = []
                actions[action].append(selection)
            for action in actions:
                info_dict.update(action_dict[action](actions[action]))
        print(info_dict)
        # TODO use info_dict to perform necessary actions

        return
