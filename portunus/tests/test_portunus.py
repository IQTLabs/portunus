# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import textwrap

import pytest

from portunus.portunus import Portunus
from portunus.tests.helpers import create_example_fixture
from portunus.tests.helpers import keys


portunus_app = create_example_fixture('bin/portunus')


def test_portunus(portunus_app):
    portunus_app.expect(textwrap.dedent("""\
        ? What do you want to do?  (<up>, <down> to move, <space> to select, <a> to togg
           ---START---
         ❯● Start Containers
          ○ Start VMs
           ---CLEANUP---
          ○ Cleanup Containers
          ○ Cleanup VMs
          ○ Cleanup Networks
          - Cleanup Portunus (Not implemented yet)
           ---INSTALL---
          ○ Install Dependencies"""))
    # pytype: disable=attribute-error
    portunus_app.writeline(keys.SPACE)
    portunus_app.writeline(keys.ENTER)
    # pytype: enable=attribute-error


def test_network_q_set_1():
    a = Portunus()
    answers = a.network_q_set_1(1)
    assert isinstance(answers, list)


def test_network():

    class MockPortunus(Portunus):

        @staticmethod
        def execute_command(command, message, change_dir=None, failok=False, shell=False):
            return 0

        @staticmethod
        def output_command(command):
            return ''

        @staticmethod
        def execute_prompt(questions):
            return {'network_exist': False, 'gauge_1': True, 'network_name_1': 'foo', 'faucet_ip': '192.168.1.1', 'network_mode_1': 'nat', 'network_options': {'Specify Datapath ID': True, 'Specify NIC to attach to the network (external connectivity if not using NAT)': True}, 'faucet_port': '6653', 'gauge_ip': '192.168.1.1', 'gauge_port': '6654', 'network_subnet_1': '192.168.0.0/24', 'network_gateway_1': '192.168.0.1', 'network_range_1': '192.168.0.0/24', 'network_dpid_1': '0x2', 'network_nic_1': 'en0', 'network_nic_port_1': '1', 'container_ssh_username_1': 'foo', 'remote_image_1': 'https://fooo.img', 'num_vms_1': 2, 'vm_basename_1': 'foo', 'vm_imagesize_1': '10g', 'vm_ssh_key_1': 'foo', 'vm_ssh_username_1': 'foo', 'vm_image_1': True, 'local_image_1': 'foo', 'vm_os_1': 'ubuntu18.04', 'vm_ramsize_1': '1024', 'vm_cpus_1': '2', 'network_dhcp_1': True, 'network_ip_options': {'Specify Subnet': True, 'Specify Gateway': True, 'Specify IP Range': True}}

    mock_portunus = MockPortunus()
    mock_portunus.get_network_info(1, {'vms': True})
    os.remove('portunus-ovs-vsctl')
    os.remove('user-data')


def test_install():

    class MockPortunus(Portunus):

        @staticmethod
        def simple_command(command):
            return

        @staticmethod
        def execute_command(command, message, change_dir=None, failok=False, shell=False):
            return 0

        @staticmethod
        def execute_prompt(questions):
            return {'network_exist': False, 'gauge_1': True, 'network_name_1': 'foo', 'faucet_ip': '192.168.1.1', 'network_mode_1': 'nat', 'network_options': {'Specify Subnet': True}, 'faucet_port': '6653', 'gauge_ip': '192.168.1.1', 'gauge_port': '6654', 'dovesnap_path': 'foo', 'ovs_install': False, 'ovs_path': 'foo', 'faucet_install': False, 'monitoring_install': False, 'gauge_install': True, 'frpc_ip': '192.168.1.1', 'mirror_in': 'eth1', 'mirror_out': 'eth0'}

    mock_portunus = MockPortunus()
    mock_portunus.install_info({})


def test_clean():
    portunus = Portunus()
    portunus.cleanup_info({'containers': True, 'networks': True, 'vms': True})


def test_main():

    class MockPortunus(Portunus):

        @staticmethod
        def execute_command(command, message, change_dir=None, failok=False, shell=False):
            return 0

        @staticmethod
        def execute_prompt(questions):
            return {'network_exist': False, 'gauge_1': True, 'network_name_1': 'foo', 'faucet_ip': '192.168.1.1', 'network_mode_1': 'nat', 'network_options': {'Specify Subnet': True}, 'faucet_port': '6653', 'gauge_ip': '192.168.1.1', 'gauge_port': '6654', 'intro': {'start containers': True}, 'num_networks': 2, 'num_containers_1': 1, 'container_image_1': 'foo', 'network_name_2': 'foo', 'network_mode_2': 'flat', 'num_containers_2': 0, 'network_dhcp_1': False, 'network_dhcp_2': True, 'network_ip_options': {'Specify Subnet': True}}

    mock_portunus = MockPortunus()
    mock_portunus.main()


def test_get_first_docker_network():
    portunus = Portunus()
    network = portunus.get_first_docker_network()
    assert network == ''
