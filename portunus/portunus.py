from __future__ import print_function
from __future__ import unicode_literals

import os
import subprocess
import sys
from pprint import pprint

import docker
import inflect
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
        self.info = {}
        self.p = inflect.engine()
        self.main()

    @staticmethod
    def execute_command(command, message, change_dir=None, failok=False):
        print(message)
        wd = None
        return_code = None
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
        except Exception as e:
            if failok:
                return_code = 0
            else:
                print(f'Command "{" ".join(command)}" failed because: {e}!')
                return_code = 1

        if return_code == None:
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
        if failok:
            return_code = 0
        return return_code

    @staticmethod
    def find_docker_networks(*args):
        client = docker.from_env()
        networks = client.networks.list('', filters={'driver': 'ovs'})
        return [network.name for network in networks]

    def get_first_docker_network(self, *args):
        networks = self.find_docker_networks()
        if networks:
            return networks[0]
        else:
            return ''

    @staticmethod
    def start_container(name, image, network):
        try:
            client = docker.from_env()
            container = client.containers.run(image=image, network=network,
                                              name=name, remove=True,
                                              detach=True)
        except Exception as e:
            print(f'Failed to start {name} because: {e}')
        print(f'Started {name}')

    def get_network_info(self, val):

        self.p.ordinal(val)
        network_question = [
            {
                'type': 'confirm',
                'name': 'network_exist',
                'default': False,
                'message': f'Does the {self.p.ordinal(val)} network already exist?',
            },
        ]
        answers = prompt(network_question, style=custom_style_2)
        if answers:
            self.info.update(answers)
            if 'network_exist' in answers and answers['network_exist']:
                docker_network = [
                    {
                        'type': 'input',
                        'name': f'network_name_{val}',
                        'default': self.get_first_docker_network,
                        'validate': DockerNetworkValidator,
                        'message': 'What is the name of the Docker OVS Network? ' + str(self.find_docker_networks()),
                    },
                ]
                answers = prompt(docker_network, style=custom_style_2)
                if answers:
                    self.info.update(answers)
                else:
                    sys.exit(0)
            else:
                network_details = [
                    {
                        'type': 'input',
                        'name': f'network_name_{val}',
                        'default': f'portunus_{val}',
                        'message': f'What name would you like the {self.p.ordinal(val)} network to be called?',
                    },
                ]
                answers = prompt(network_details, style=custom_style_2)
                if answers:
                    self.info.update(answers)
                else:
                    sys.exit(0)
                network_options = [
                    {
                        'type': 'confirm',
                        'name': f'network_mode_{val}',
                        'default': 'True',
                        'message': f'Do you want network {self.info["network_name_"+str(val)]} to use NAT?',
                    },
                    {
                        'type': 'checkbox',
                        'name': 'network_options',
                        'message': f'What options do you want specify for network {self.info["network_name_"+str(val)]}?',
                        'choices': [
                            {'name': 'Specify Subnet', 'checked': True},
                            {'name': 'Specify Gateway'},
                            {'name': 'Specify IP Range'},
                            {'name': 'Specify Datapath ID'},
                            {'name': 'Specify NIC to attach to the network (external connectivity if not using NAT)'},
                        ],
                    },
                ]
                answers = prompt(network_options, style=custom_style_2)
                if answers:
                    self.info.update(answers)
                else:
                    sys.exit(0)
                network_mode = 'nat' if self.info[f'network_mode_{val}'] else 'flat'
                create_network = ['docker', 'network', 'create', '-d',
                                  'ovs', '-o', f'ovs.bridge.mode={network_mode}']
                network_questions = []
                answers = answers['network_options']
                if 'Specify Subnet' in answers:
                    network_questions.append(
                        {
                            'type': 'input',
                            'name': f'network_subnet_{val}',
                            'default': '192.168.10.0/24',
                            'message': f'What do you want to make the subnet be for {self.info["network_name_"+str(val)]}?',
                        }
                    )
                if 'Specify Gateway' in answers:
                    network_questions.append(
                        {
                            'type': 'input',
                            'name': f'network_gateway_{val}',
                            'default': '192.168.10.254',
                            'message': f'What do you want to make the gateway be for {self.info["network_name_"+str(val)]}?',
                        },
                    )
                if 'Specify IP Range' in answers:
                    network_questions.append(
                        {
                            'type': 'input',
                            'name': f'network_range_{val}',
                            'default': '192.168.10.10/24',
                            'message': f'What do you want to make the IP range be for {self.info["network_name_"+str(val)]}?',
                        },
                    )
                if 'Specify Datapath ID' in answers:
                    network_questions.append(
                        {
                            'type': 'input',
                            'name': f'network_dpid_{val}',
                            'default': '0x1',
                            'message': f'What do you want to make the Datapath ID be for {self.info["network_name_"+str(val)]}?',
                        },
                    )
                if 'Specify NIC to attach to the network (external connectivity if not using NAT)' in answers:
                    network_questions.append(
                        {
                            'type': 'input',
                            'name': f'network_nic_{val}',
                            'default': 'eno1',
                            'message': f'What is the name of the NIC you want to attach to {self.info["network_name_"+str(val)]}?',
                        },
                    )
                if network_questions:
                    answers = prompt(network_questions, style=custom_style_2)
                    if answers:
                        self.info.update(answers)
                    else:
                        sys.exit(0)

                commands = []
                if f'network_subnet_{val}' in answers:
                    create_network += ['--subnet',
                                       answers[f'network_subnet_{val}']]
                if f'network_gateway_{val}' in answers:
                    create_network += ['--gateway',
                                       answers[f'network_gateway_{val}']]
                if f'network_range_{val}' in answers:
                    create_network += ['--ip-range',
                                       answers[f'network_range_{val}']]
                if f'network_dpid_{val}' in answers:
                    create_network += ['-o',
                                       f'ovs.bridge.dpid={answers["network_dpid_"+str(val)]}']
                # TODO add gauge
                create_network += [
                    '-o', f'ovs.bridge.controller=tcp:{self.info["faucet_ip"]}:{self.info["faucet_port"]}', self.info[f'network_name_{val}']]
                commands.append((create_network, 'creating network...'))
                if f'network_nic_{val}' in answers:
                    commands.append((['docker', 'exec', '-it', 'dovesnap_ovs_1', '/scripts/add_port.sh',
                                      answers[f'network_nic_{val}']], 'adding network interface...'))

                for command in commands:
                    if self.execute_command(command[0], command[1]) != 0:
                        sys.exit(1)
                container_questions = [
                    {
                        'type': 'input',
                        'name': f'num_containers_{val}',
                        'default': '1',
                        'message': f'How many containers do you want started on network {self.info["network_name_"+str(val)]}?',
                        'validate': NumberValidator,
                        'filter': lambda val: int(val)
                    },
                    {
                        'type': 'input',
                        'name': f'container_image_{val}',
                        # TODO this default should be an image using ssh and can be run in the background
                        'default': 'ubuntu:latest',
                        'message': 'What image would you like to use for your containers?',
                    },
                    # TODO inject ssh key? / get it from github?
                ]
                answers = prompt(container_questions, style=custom_style_2)
                if answers:
                    self.info.update(answers)
                else:
                    sys.exit(0)

                # start containers
                for c_val in range(1, answers[f'num_containers_{val}']+1):
                    self.start_container('portunus_'+self.info[f'network_name_{val}']+f'_{c_val}',
                                         self.info[f'container_image_{val}'],
                                         self.info[f'network_name_{val}'])
        else:
            sys.exit(0)

    def start_info(self, selections):
        if 'containers' in selections:
            container_questions = [
                {
                    'type': 'input',
                    'name': 'num_networks',
                    'default': '1',
                    'message': 'How many different networks do you want?',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                },
            ]
            answers = prompt(container_questions, style=custom_style_2)
            if answers:
                self.info.update(answers)
            else:
                sys.exit(0)
            # get additional info for each network
            for i in range(1, answers['num_networks']+1):
                network = self.get_network_info(i)

        if 'vms' in selections:
            # TODO ovs bridge name?
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
                self.info.update(answers)
            else:
                sys.exit(0)
            commands = [
                (['sudo', 'modprobe', 'kvm'], 'enabling kvm...'),
                (['sudo', 'modprobe', '8021q'], 'enabling 802.1q...'),
            ]
            for command in commands:
                if self.execute_command(command[0], command[1]) != 0:
                    sys.exit(1)

    @staticmethod
    def cleanup_info(selections):
        # TODO
        # containers, vms, networks, ovs/dovesnap
        return

    def setup_info(self, selections):
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
                self.info.update(answers)
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
                        self.info.update(answers)
                    else:
                        sys.exit(0)
            else:
                sys.exit(0)
        if 'monitoring' in selections:
            commands = [
                # TODO put in real commands
                (['ping', '-c 4', 'python.org'], 'setting up Monitoring...'),
            ]
            for command in commands:
                if self.execute_command(command[0], command[1]) != 0:
                    sys.exit(1)
        if 'poseidon' in selections:
            commands = [
                # TODO put in real commands
                (['ping', '-c 4', 'python.org'], 'setting up Poseidon...'),
            ]
            for command in commands:
                if self.execute_command(command[0], command[1]) != 0:
                    sys.exit(1)

    def install_info(self, selections):
        install_questions = [
            {
                'type': 'input',
                'name': 'dovesnap_path',
                'default': '/opt',
                'message': 'What path would you like to install dovesnap in?',
            },
        ]
        answers = prompt(install_questions, style=custom_style_2)
        if answers:
            self.info.update(answers)
        else:
            sys.exit(0)
        commands = [
            (['git', 'version'], 'checking git version...'),
            (['docker', 'version'], 'checking Docker version...'),
            (['docker-compose', 'version'], 'checking docker-compose version...'),
            (['sudo', 'modprobe', 'openvswitch'],
             'enabling openvswitch...', '.', True),
            (['sudo', 'modprobe', '8021q'], 'enabling 802.1q...', '.', True),
            (['sudo', 'rm', '-rf', os.path.join(answers['dovesnap_path'],
                                                'dovesnap')], 'cleaning up dovesnap...'),
            (['sudo', 'git', 'clone', 'https://github.com/cyberreboot/dovesnap'],
             'cloning dovesnap...', answers['dovesnap_path']),
            (['sudo', 'docker-compose', 'up', '-d', '--build'], 'building dovesnap...',
             os.path.join(answers['dovesnap_path'], 'dovesnap')),
        ]
        for command in commands:
            change_dir = None
            failok = False
            if len(command) == 3:
                change_dir = command[2]
            if len(command) == 4:
                failok = command[3]
            if self.execute_command(command[0], command[1], change_dir=change_dir, failok=failok) != 0:
                sys.exit(1)

    def main(self):
        question = [
            {
                'type': 'checkbox',
                'name': 'intro',
                'message': 'What do you want to do?',
                'choices': [
                    Separator(' ---START--- '),
                    {'name': 'Start Containers',
                     'checked': True},
                    {'name': 'Start VMs'},
                    Separator(' ---CLEANUP--- '),
                    {'name': 'Cleanup Containers'},
                    {'name': 'Cleanup VMs'},
                    {'name': 'Cleanup Portunus (Faucet, Monitoring, Poseidon, OVS, etc. if running)'},
                    Separator(' ---SETUP--- '),
                    {'name': 'Setup Faucet'},
                    {'name': 'Setup Monitoring', 'disabled': 'Not implemented yet.'},
                    {'name': 'Setup Poseidon', 'disabled': 'Not implemented yet.'},
                    Separator(' ---INSTALL--- '),
                    {'name': 'Install Dependencies'},
                ],
            },
        ]

        answers = prompt(question, style=custom_style_2)
        actions = {}
        action_dict = {
            'cleanup': self.cleanup_info,
            'install': self.install_info,
            'setup': self.setup_info,
            'start': self.start_info
        }
        if 'intro' in answers:
            answers = answers['intro']
            if 'Start Containers' in answers or 'Start VMs' in answers:
                # if something is being started, ensure things are setup
                actions['setup'] = []

            for answer in answers:
                action, selection = answer.lower().split()
                if action not in actions:
                    actions[action] = []
                actions[action].append(selection)
            action_order = []
            for action in actions:
                action_order.append(action)
            action_order.sort()
            for action in action_order:
                action_dict[action](actions[action])
            print(self.info)
