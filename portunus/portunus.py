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
from portunus.validators import PortValidator


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
        def network_mode_message(answers):
            return 'Do you want network '+answers['network_name_'+str(val)]+' to use NAT?'

        def network_options_message(answers):
            return f'What options do you want specify for network {answers["network_name_"+str(val)]}?'
        answers = None
        network_questions = [
            {
                'type': 'confirm',
                'name': 'network_exist',
                'default': False,
                'message': f'Does the {self.p.ordinal(val)} network already exist?',
            },
            {
                'type': 'input',
                'name': f'network_name_{val}',
                'default': self.get_first_docker_network,
                'validate': DockerNetworkValidator,
                'when': lambda answers: answers['network_exist'],
                'message': 'What is the name of the Docker OVS Network? ' + str(self.find_docker_networks()),
            },
            {
                'type': 'input',
                'name': f'network_name_{val}',
                'default': f'portunus_{val}',
                'when': lambda answers: not answers['network_exist'],
                'message': f'What name would you like the {self.p.ordinal(val)} network to be called?',
            },
            {
                'type': 'confirm',
                'name': f'network_mode_{val}',
                'default': 'True',
                'when': lambda answers: not answers['network_exist'],
                'message': f'Do you want the {self.p.ordinal(val)} network to use NAT?',
            },
            {
                'type': 'checkbox',
                'name': 'network_options',
                'when': lambda answers: not answers['network_exist'],
                'message': f'What options do you want specify for the {self.p.ordinal(val)} network?',
                'choices': [
                    {'name': 'Specify Subnet', 'checked': True},
                    {'name': 'Specify Gateway'},
                    {'name': 'Specify IP Range'},
                    {'name': 'Specify Datapath ID'},
                    {'name': 'Specify NIC to attach to the network (external connectivity if not using NAT)'},
                ],
            },
        ]
        answers = prompt(network_questions, style=custom_style_2)
        if answers:
            self.info.update(answers)
        else:
            sys.exit(0)
        if not answers['network_exist']:
            self.faucet_info(val)
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
                    {
                        'type': 'input',
                        'name': f'network_nic_port_{val}',
                        'default': '1',
                        'message': f'What OpenFlow port should OVS try to assign this NIC to? (not guaranteed)',
                        'validate': PortValidator,
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
            if f'network_nic_{val}' in answers:
                create_network += ['-o',
                                   f'ovs.bridge.add_ports={answers["network_nic_"+str(val)]}/{answers["network_nic_port"+str(val)]}']

            controller = 'ovs.bridge.controller=tcp:' + \
                self.info[f'faucet_ip_{val}']+':' + \
                self.info[f'faucet_port_{val}']
            if self.info[f'gauge_{val}']:
                controller += ',tcp:' + \
                    self.info[f'gauge_ip_{val}']+':' + \
                    self.info[f'gauge_port_{val}']
            create_network += [
                '-o', controller, self.info[f'network_name_{val}']]
            commands.append((create_network, 'creating network...'))

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
                'when': lambda answers: answers[f'num_containers_{val}'] > 0,
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

    def faucet_info(self, val):
        faucet_questions = [
            {
                'type': 'input',
                'name': f'faucet_ip_{val}',
                'validate': IPValidator,
                'message': 'What is the IP of Faucet you\'d like to connect to '+self.info[f'network_name_{val}']+'?',
            },
            {
                'type': 'input',
                'name': f'faucet_port_{val}',
                'default': '6653',
                'message': 'What port is Faucet running on?',
                'validate': PortValidator,
            },
            {
                'type': 'confirm',
                'name': f'gauge_{val}',
                'default': True,
                'message': 'Is Gauge being used for '+self.info[f'network_name_{val}']+'?',
            },
        ]
        answers = prompt(faucet_questions, style=custom_style_2)
        if answers:
            self.info.update(answers)
            if f'gauge_{val}' in answers and answers[f'gauge_{val}']:
                gauge_questions = [
                    {
                        'type': 'input',
                        'name': f'gauge_ip_{val}',
                        'default': answers[f'faucet_ip_{val}'],
                        'validate': IPValidator,
                        'message': 'What is the IP of Gauge you\'d like to connect to '+self.info[f'network_name_{val}']+'?',
                    },
                    {
                        'type': 'input',
                        'name': f'gauge_port_{val}',
                        'default': '6654',
                        'message': 'What port is Gauge running on?',
                        'validate': PortValidator,
                    },
                ]
                answers = prompt(gauge_questions, style=custom_style_2)
                if answers:
                    self.info.update(answers)
                else:
                    sys.exit(0)
        else:
            sys.exit(0)

    def setup_info(self, selections):
        if 'faucet' in selections:
            commands = [
                # TODO put in real commands
                (['ping', '-c 4', 'python.org'], 'setting up Faucet...'),
            ]
            for command in commands:
                if self.execute_command(command[0], command[1]) != 0:
                    sys.exit(1)
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
                    {'name': 'Cleanup Containers',
                        'disabled': 'Not implemented yet'},
                    {'name': 'Cleanup VMs', 'disabled': 'Not implemented yet'},
                    {'name': 'Cleanup Portunus (Faucet, Monitoring, Poseidon, OVS, etc. if running)',
                     'disabled': 'Not implemented yet'},
                    Separator(' ---SETUP--- '),
                    {'name': 'Setup Faucet', 'disabled': 'Not implemented yet'},
                    {'name': 'Setup Monitoring', 'disabled': 'Not implemented yet'},
                    {'name': 'Setup Poseidon', 'disabled': 'Not implemented yet'},
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
