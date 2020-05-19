from __future__ import print_function
from __future__ import unicode_literals

import os
import subprocess
import sys
from pprint import pprint

import docker
from examples import custom_style_2
from PyInquirer import prompt
from PyInquirer import Separator
from PyInquirer import style_from_dict
from PyInquirer import Token

from portunus.validators import DockerNetworkValidator
from portunus.validators import IPValidator
from portunus.validators import KVMImageValidator
from portunus.validators import NumberValidator


class Portunus():

    def __init__(self):
        self.main()

    @staticmethod
    def execute_command(command, message, change_dir=None):
        print(message)
        wd = None
        if change_dir:
            try:
                wd = os.getcwd()
                os.chdir(change_dir)
            except Exception as e:
                print(
                    f'Unable to change to directory {change_dir} because {e}')
                return 1
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

        if change_dir:
            try:
                os.chdir(wd)
            except Exception as e:
                print(f'Unable to change to directory {wd} because {e}')
                return 1
        return return_code

    @staticmethod
    def find_docker_network(*args):
        client = docker.from_env()
        networks = client.networks.list('', filters={'driver': 'ovs'})
        if len(networks) > 0:
            return networks[0].name
        else:
            return ''

    @staticmethod
    def start_info(selections, start_types):
        # TODO
        return {}

    @staticmethod
    def cleanup_info(selections, start_types):
        # TODO
        return {}

    def setup_info(self, selections, start_types):
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
            if answers:
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
                    if answers:
                        info.update(answers)
                    else:
                        sys.exit(0)
            else:
                sys.exit(0)
        if 'docker' in selections:
            commands = [
                # TODO put in real commands
                (['ping', '-c 4', 'python.org'], 'setting up Docker...'),
            ]
            for command in commands:
                if self.execute_command(command[0], command[1]) != 0:
                    sys.exit(1)
        elif 'containers' in start_types and 'ovs' not in selections:
            docker_questions = [
                {
                    'type': 'input',
                    'name': 'docker_network',
                    'default': self.find_docker_network,
                    'validate': DockerNetworkValidator,
                    'message': 'What is the name of the Docker OVS Network?',
                },
            ]
            answers = prompt(docker_questions, style=custom_style_2)
            if answers:
                info.update(answers)
            else:
                sys.exit(0)

        if 'kvm' in selections:
            print('kvm')
            # TODO
        elif 'vms' in start_types:
            kvm_questions = [
                {
                    'type': 'input',
                    'name': 'kvm_image',
                    'validate': KVMImageValidator,
                    'message': 'What is the path to the KVM image you wish to use?',
                },
            ]
            answers = prompt(kvm_questions, style=custom_style_2)
            if answers:
                info.update(answers)
            else:
                sys.exit(0)
            commands = [
                (['sudo', 'modprobe', 'kvm'], 'enabling kvm...'),
                (['sudo', 'modprobe', '8021q'], 'enabling 802.1q...'),
            ]
            for command in commands:
                if self.execute_command(command[0], command[1]) != 0:
                    sys.exit(1)
        if 'ovs' in selections:
            ovs_questions = [
                {
                    'type': 'input',
                    'name': 'dovesnap_path',
                    'default': '/tmp',
                    'message': 'What path would you like to install dovesnap in?',
                },
                {
                    'type': 'input',
                    'name': 'dovesnap_network',
                    'default': 'dovesnap',
                    'message': 'What name would you like the network to be called?',
                },
                {
                    'type': 'input',
                    'name': 'dovesnap_gateway',
                    'default': '192.168.10.254',
                    'message': 'What is the gateway for this network?',
                },
                {
                    'type': 'input',
                    'name': 'dovesnap_subnet',
                    'default': '192.168.10.0/24',
                    'message': 'What is the subnet for this network?',
                },
                {
                    'type': 'input',
                    'name': 'dovesnap_range',
                    'default': '192.168.10.10/24',
                    'message': 'What is the IP range for this network?',
                },
                {
                    'type': 'input',
                    'name': 'dovesnap_nic',
                    'default': 'eno1',
                    'message': 'Do you have a NIC to attach to this network?',
                },
            ]
            answers = prompt(ovs_questions, style=custom_style_2)
            if answers:
                info.update(answers)
            else:
                sys.exit(0)
            commands = [
                (['sudo', 'modprobe', 'openvswitch'], 'enabling openvswitch...'),
                (['sudo', 'modprobe', '8021q'], 'enabling 802.1q...'),
                # move this to cleanup
                (['sudo', 'rm', '-rf', os.path.join(answers['dovesnap_path'],
                                                    'dovesnap')], 'cleaning up dovesnap...'),
                # TODO put in a real path
                (['git', 'clone', 'https://github.com/cglewis/dovesnap'],
                 'cloning dovesnap...', answers['dovesnap_path']),
                (['docker-compose', 'up', '-d', '--build'], 'building dovesnap...',
                 os.path.join(answers['dovesnap_path'], 'dovesnap')),
                # TODO make arguments for these options
                (['docker', 'network', 'create', '--gateway', answers['dovesnap_gateway'], '--subnet', answers['dovesnap_subnet'],
                  '--ip-range', answers['dovesnap_range'], '-d', 'ovs', answers['dovesnap_network']], 'creating network...'),
                (['docker', 'exec', '-it', 'dovesnap_ovs_1', '/scripts/add_port.sh',
                  answers['dovesnap_nic']], 'adding network interface...'),
                (['docker', 'exec', '-it', 'dovesnap_ovs_1', '/scripts/add_controller.sh', 'tcp:'+info['faucet_ip']+':' + \
                  str(info['faucet_port']), 'tcp:'+info['gauge_ip']+':'+str(info['gauge_port'])], 'adding controller...'),
            ]
            for command in commands:
                change_dir = None
                if len(command) == 3:
                    change_dir = command[2]
                if self.execute_command(command[0], command[1], change_dir=change_dir) != 0:
                    sys.exit(1)
        else:
            # TODO
            print('already have ovs setup')

        return info

    @staticmethod
    def install_info(selections, start_types):
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
        actions = {}
        action_dict = {
            'start': self.start_info,
            'cleanup': self.cleanup_info,
            'setup': self.setup_info,
            'install': self.install_info
        }
        if 'intro' in answers:
            answers = answers['intro']
            start_types = []
            if 'Start Containers' in answers:
                start_types.append('containers')
            if 'Start VMs' in answers:
                start_types.append('vms')

            # if something is being started, ensure dependencies are good to go
            if start_types:
                # note install isn't included because it isn't implemented yet
                actions['cleanup'] = []
                actions['start'] = []
                actions['setup'] = []

            for answer in answers:
                action, selection = answer.lower().split()
                if action not in actions:
                    actions[action] = []
                actions[action].append(selection)
            for action in actions:
                info_dict.update(action_dict[action](
                    actions[action], start_types))
            print(info_dict)

        # TODO use info_dict to perform necessary actions

        return
