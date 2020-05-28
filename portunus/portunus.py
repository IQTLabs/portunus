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
from portunus.validators import ImageValidator
from portunus.validators import IPValidator
from portunus.validators import NumberValidator
from portunus.validators import PortValidator


class Portunus():

    def __init__(self):
        self.info = {}
        self.p = inflect.engine()
        self.main()

    @staticmethod
    def execute_command(command, message, change_dir=None, failok=False, shell=False):
        print(message)
        # TODO add logging, and make this a DEBUG statement
        #print(' '.join(command))
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
                                       universal_newlines=True, shell=shell)
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
    def start_container(name, image, network, command=None):
        try:
            client = docker.from_env()
            container = client.containers.run(image=image, network=network,
                                              name=name, remove=True,
                                              detach=True)
            if command:
                container.exec_run(command)
        except Exception as e:
            print(f'Failed to start {name} because: {e}')
        print(f'Started {name}')

    def get_network_info(self, val, selections):
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
                'message': f'Do you want the {self.p.ordinal(val)} network to use NAT (only available for containers)?',
            },
            {
                'type': 'checkbox',
                'name': 'network_options',
                'when': lambda answers: not answers['network_exist'],
                'message': f'What options do you want to specify for the {self.p.ordinal(val)} network?',
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
                    }
                )
                network_questions.append(
                    {
                        'type': 'input',
                        'name': f'network_nic_port_{val}',
                        'default': '1',
                        'message': f'What OpenFlow port should OVS try to assign this NIC to? (not guaranteed)',
                        'validate': PortValidator,
                    }
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
                                   f'ovs.bridge.add_ports={answers["network_nic_"+str(val)]}/{answers["network_nic_port_"+str(val)]}']

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

        if 'containers' in selections:
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
                    'default': 'cyberreboot/ssh_server:latest',
                    'when': lambda answers: answers[f'num_containers_{val}'] > 0,
                    'message': 'What image would you like to use for your containers?',
                },
                {
                    'type': 'confirm',
                    'name': f'container_ssh_key_{val}',
                    'default': True,
                    'message': 'Would you like to add your SSH key from GitHub to the containers?',
                },
                {
                    'type': 'input',
                    'name': f'container_ssh_username_{val}',
                    'when': lambda answers: answers[f'container_ssh_key_{val}'],
                    'message': 'What is your GitHub username?',
                },
            ]
            answers = prompt(container_questions, style=custom_style_2)
            if answers:
                self.info.update(answers)
            else:
                sys.exit(0)

            # start containers
            for c_val in range(1, answers[f'num_containers_{val}']+1):
                command = None
                if f'container_ssh_username_{val}' in self.info:
                    command = 'bash -c "curl https://github.com/' + \
                        self.info[f'container_ssh_username_{val}'] + \
                        '.keys >> ~/.ssh/authorized_keys"'
                self.start_container('portunus_'+self.info[f'network_name_{val}']+f'_{c_val}',
                                     self.info[f'container_image_{val}'],
                                     self.info[f'network_name_{val}'], command=command)
        if 'vms' in selections:
            commands = [
                (['sudo', 'modprobe', 'kvm'], 'enabling KVM...'),
                (['sudo', 'modprobe', '8021q'], 'enabling 802.1q...'),
                (['kvm-ok'], 'checking KVM...'),
                (['sudo', 'mkdir', '-p', '/var/lib/libvirt/images/base'],
                 'ensuring base directory exists...'),
            ]
            vm_questions = [
                {
                    'type': 'input',
                    'name': f'num_vms_{val}',
                    'default': '1',
                    'message': f'How many VMs do you want started on network {self.info["network_name_"+str(val)]}?',
                    'validate': NumberValidator,
                    'filter': lambda val: int(val)
                },
                {
                    'type': 'confirm',
                    'name': f'vm_image_{val}',
                    'default': False,
                    'message': f'Do you already have an image locally you want to use for network {self.info["network_name_"+str(val)]}?',
                },
                {
                    'type': 'input',
                    'name': f'local_image_{val}',
                    'validate': ImageValidator,
                    'message': 'What is the path to the image you wish to use?',
                    'when': lambda answers: answers[f'vm_image_{val}']
                },
                {
                    'type': 'input',
                    'name': f'remote_image_{val}',
                    'message': 'What is the URL to the image you wish to use?',
                    'when': lambda answers: not answers[f'vm_image_{val}']
                },
                {
                    'type': 'input',
                    'name': f'vm_basename_{val}',
                    'message': f'What basename do you want for your VM(s) for network {self.info["network_name_"+str(val)]}?',
                },
                {
                    'type': 'input',
                    'name': f'vm_imagesize_{val}',
                    # TODO needs validation
                    'default': '5G',
                    'message': f'What size disk do you want for your VM(s) for network {self.info["network_name_"+str(val)]}?',
                },
                {
                    'type': 'input',
                    'name': f'vm_ramsize_{val}',
                    # TODO needs validation
                    'default': '1024',
                    'message': f'How much RAM (in MB) do you want for your VM(s) for network {self.info["network_name_"+str(val)]}?',
                },
                {
                    'type': 'input',
                    'name': f'vm_cpus_{val}',
                    # TODO needs validation
                    'default': '1',
                    'message': f'How many CPUs do you want for your VM(s) for network {self.info["network_name_"+str(val)]}?',
                },
                {
                    'type': 'input',
                    'name': f'vm_os_{val}',
                    # TODO needs validation
                    'default': 'None',
                    'message': f'What is the OS variant (i.e. ubuntu16.04) for your VM(s) for network {self.info["network_name_"+str(val)]} (Use None if you don\'t know)?',
                },
                {
                    'type': 'confirm',
                    'name': f'vm_ssh_key_{val}',
                    'default': True,
                    'message': 'Would you like to add your SSH key from GitHub to the VMs?',
                },
                {
                    'type': 'input',
                    'name': f'vm_ssh_username_{val}',
                    'when': lambda answers: answers[f'vm_ssh_key_{val}'],
                    'message': 'What is your GitHub username?',
                },
            ]
            answers = prompt(vm_questions, style=custom_style_2)
            if answers:
                self.info.update(answers)
            else:
                sys.exit(0)

            qcow2 = ''
            if f'vm_image_{val}' in answers and answers[f'vm_image_{val}']:
                # copy existing image
                qcow2 = os.path.basename(
                    answers[f'local_image_{val}']).replace('.img', '.qcow2')
                commands.append(
                    (['sudo', 'cp', answers[f'local_image_{val}'], f'/var/lib/libvirt/images/base/{qcow2}'], 'copying image...'))
            else:
                # download image then move
                commands.append(
                    (['wget', answers[f'remote_image_{val}']], 'downloading image...'))
                qcow2 = os.path.basename(
                    answers[f'remote_image_{val}']).replace('.img', '.qcow2')
                commands.append((['sudo', 'mv', os.path.basename(
                    answers[f'remote_image_{val}']), f'/var/lib/libvirt/images/base/{qcow2}'], 'moving image...'))

            for vm in range(1, answers[f'num_vms_{val}']+1):
                vm_commands = [
                    # create directory for vm
                    (['sudo', 'mkdir', '-p', '/var/lib/libvirt/images/' + \
                      answers[f'vm_basename_{val}']+f'-{vm}'], 'creating directory for new VM...'),
                    # create vm image
                    (['sudo', 'qemu-img', 'create', '-f', 'qcow2', '-F', 'qcow2', '-o',
                      f'backing_file=/var/lib/libvirt/images/base/{qcow2}', '/var/lib/libvirt/images/'+answers[f'vm_basename_{val}']+f'-{vm}/'+answers[f'vm_basename_{val}']+f'-{vm}.qcow2'], 'creating directory for new VM...'),
                    # resize image
                    (['sudo', 'qemu-img', 'resize', '/var/lib/libvirt/images/' + \
                      answers[f'vm_basename_{val}']+f'-{vm}/'+answers[f'vm_basename_{val}']+f'-{vm}.qcow2', answers[f'vm_imagesize_{val}']], 'resizing image...'),
                    # create meta-data
                    (['echo "local-hostname: ' + \
                      answers[f'vm_basename_{val}']+f'-{vm}" > meta-data'], 'create meta-data...', True),
                    # create user-data file
                ]
                commands += vm_commands

                # create user-data
                ssh_key = {'auth_key': ''}
                if answers[f'vm_ssh_key_{val}']:
                    pub_key = subprocess.check_output(
                        'wget -qO- https://github.com/'+self.info[f'vm_ssh_username_{val}']+'.keys', shell=True)
                    pub_key = pub_key.decode('utf-8').rstrip('\n')
                    ssh_key['auth_key'] = f'ssh-authorized-keys:\n      - {pub_key}'
                cloud_config = """#cloud-config

users:
  - name: ubuntu
    %(auth_key)s
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    groups: sudo
    shell: /bin/bash
runcmd:
  - echo "AllowUsers ubuntu" >> /etc/ssh/sshd_config
  - restart ssh
""" % ssh_key
                with open('user-data', 'w') as f:
                    f.write(cloud_config)

                ovs_vsctl = subprocess.check_output(
                    'which ovs-vsctl', shell=True)
                ovs_vsctl = ovs_vsctl.decode('utf-8').rstrip('\n')
                ovs_wrapper = """#!/bin/bash

%s-orig --db=tcp:127.0.0.1:6640 $@
""" % ovs_vsctl
                with open('portunus-ovs-vsctl', 'w') as f:
                    f.write(ovs_wrapper)
                client = docker.from_env()
                network = client.networks.get(self.info[f'network_name_{val}'])
                bridge = 'ovsbr-'+network.id[:5]
                os_variant = 'generic'
                if answers[f'vm_os_{val}'] is not 'None':
                    os_variant = answers[f'vm_os_{val}']
                vm_commands = [
                    # create iso
                    (['sudo', 'genisoimage', '-output', '/var/lib/libvirt/images/' + \
                      answers[f'vm_basename_{val}']+f'-{vm}/'+answers[f'vm_basename_{val}']+f'-{vm}-cidata.iso', '-volid', 'cidata', '-joliet', '-rock', 'user-data', 'meta-data'], 'create iso...'),
                    # remove data files
                    (['rm', 'meta-data'], 'removing meta-data...'),
                    (['rm', 'user-data'], 'removing user-data...'),
                    # hack that wraps ovs-vsctl due to libvirt hard-coding it
                    (['chmod', '+x', 'portunus-ovs-vsctl'],
                     'making ovs-vsctl wrapper executable...'),
                    (['sudo', 'mv', ovs_vsctl, ovs_vsctl+'-orig'],
                     'moving ovs-vsctl to ovs-vsctl-orig...'),
                    (['sudo', 'mv', 'portunus-ovs-vsctl', ovs_vsctl],
                     'moving wrapper to ovs-vsctl...'),
                    # create vm
                    (['virt-install',
                      '--connect', 'qemu:///system',
                      '--virt-type', 'kvm',
                      '--name', answers[f'vm_basename_{val}']+f'-{vm}',
                      '--memory', answers[f'vm_ramsize_{val}'],
                      '--vcpus='+answers[f'vm_cpus_{val}'],
                      '--os-variant', os_variant,
                      '--disk', 'path=/var/lib/libvirt/images/' + \
                      answers[f'vm_basename_{val}']+f'-{vm}/' + \
                      answers[f'vm_basename_{val}'] + \
                      f'-{vm}.qcow2,format=qcow2',
                      '--disk', '/var/lib/libvirt/images/' + \
                      answers[f'vm_basename_{val}']+f'-{vm}/' + \
                      answers[f'vm_basename_{val}'] + \
                      f'-{vm}-cidata.iso,device=cdrom',
                      '--import',
                      '--network', f'bridge={bridge},virtualport_type=openvswitch',
                      '--noautoconsole'], 'create vm...'),
                    # put ovs-vsctl back
                    (['sudo', 'mv', ovs_vsctl+'-orig', ovs_vsctl],
                     'moving ovs-vsctl-orig back to ovs-vsctl...'),
                ]
                commands += vm_commands

            for command in commands:
                shell = False
                if len(command) == 3:
                    shell = command[2]
                if self.execute_command(command[0], command[1], shell=shell) != 0:
                    sys.exit(1)

    def start_info(self, selections):
        start_questions = [
            {
                'type': 'input',
                'name': 'num_networks',
                'default': '1',
                'message': 'How many different networks do you want?',
                'validate': NumberValidator,
                'filter': lambda val: int(val)
            },
        ]
        answers = prompt(start_questions, style=custom_style_2)
        if answers:
            self.info.update(answers)
        else:
            sys.exit(0)
        # get additional info for each network
        for i in range(1, answers['num_networks']+1):
            network = self.get_network_info(i, selections)

    def cleanup_info(self, selections):
        client = docker.from_env()
        networks = client.networks.list(filters={'driver': 'ovs'})
        if 'containers' in selections:
            container_choices = []
            for network in networks:
                containers = client.containers.list(
                    filters={'network': network.name})
                for container in containers:
                    container_choices.append(
                        {'name': f'{container.name} ({network.name})'})
            question = [
                {
                    'type': 'checkbox',
                    'name': 'cleanup_containers',
                    'message': 'Which containers would you like to remove?',
                    'choices': container_choices,
                },
            ]

            answers = prompt(question, style=custom_style_2)
            if 'cleanup_containers' in answers:
                answers = answers['cleanup_containers']
                for answer in answers:
                    container_name = answer.split()[0]
                    c = client.containers.get(container_name)
                    c.remove(force=True)
        if 'networks' in selections:
            network_choices = []
            network_containers = {}
            for network in networks:
                network_containers[network.name] = []
                containers = client.containers.list(
                    filters={'network': network.name})
                for container in containers:
                    network_containers[network.name].append(container.name)
                # TODO get VMs
                network_choices.append(
                    {'name': f'{network.name} ({len(containers)} {self.p.plural("container", len(containers))})'})
            if networks:
                question = [
                    {
                        'type': 'checkbox',
                        'name': 'cleanup_networks',
                        'message': 'Which networks (and their containers/VMs) would you like to remove?',
                        'choices': network_choices,
                    },
                ]

                answers = prompt(question, style=custom_style_2)
                if 'cleanup_networks' in answers:
                    answers = answers['cleanup_networks']
                    for answer in answers:
                        network_name = answer.split()[0]
                        for container_name in network_containers[network_name]:
                            c = client.containers.get(container_name)
                            c.remove(force=True)
                        n = client.networks.get(network_name)
                        n.remove()
        # TODO vms, ovs/dovesnap
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
            # debian specific
            (['sudo', 'apt-get', 'update'],
             'updating package sources...', '.', True),
            (['sudo', 'apt-get', 'install', '-y', 'qemu-kvm', 'libvirt-bin', 'qemu-utils',
              'genisoimage', 'virtinst', 'wget'], 'installing packages for KVM...', '.', True),
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
        print('NOTE: For VMs, apparmor profiles will need to be modified for libvirt, the easiest (though less secure option is to set `security_driver = "none"` in `/etc/libvirt/qemu.conf`.')
        print('NOTE: For starting VMs you will need Open vSwitch installed locally first.')
        print('NOTE: For VMs to connect to OVS bridges that are not local `ovs-vsctl` is wrapped and the original command is moved to `ovs-vsctl-orig`. This will temporarily happen only when starting VMs, then be put back.')

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
                    {'name': 'Cleanup VMs', 'disabled': 'Not implemented yet'},
                    {'name': 'Cleanup Networks'},
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
