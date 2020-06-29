# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import textwrap

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
          - Cleanup Portunus (Faucet, Monitoring, Poseidon, OVS, etc. if running) (Not i
           ---SETUP---
          - Setup Faucet (Not implemented yet)
          - Setup Monitoring (Not implemented yet)
          - Setup Poseidon (Not implemented yet)
           ---INSTALL---
          ○ Install Dependencies"""))
    portunus_app.writeline(keys.SPACE)
    portunus_app.writeline(keys.ENTER)


def test_setup_info():
    a = Portunus()
    a.setup_info(['faucet', 'monitoring', 'poseidon'])


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
        def execute_prompt(questions):
            return {'network_exist': False, 'gauge_1': True, 'network_name_1': 'foo', 'faucet_ip_1': '192.168.1.1', 'network_mode_1': 'nat', 'network_options': {'Specify Subnet': True}, 'faucet_port_1': '6653', 'gauge_ip_1': '192.168.1.1', 'gauge_port_1': '6654'}

    mock_portunus = MockPortunus()
    mock_portunus.get_network_info(1, {})


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
            return {'network_exist': False, 'gauge_1': True, 'network_name_1': 'foo', 'faucet_ip_1': '192.168.1.1', 'network_mode_1': 'nat', 'network_options': {'Specify Subnet': True}, 'faucet_port_1': '6653', 'gauge_ip_1': '192.168.1.1', 'gauge_port_1': '6654', 'dovesnap_path': 'foo', 'ovs_install': False, 'ovs_path': 'foo'}

    mock_portunus = MockPortunus()
    mock_portunus.install_info({})


def test_clean():
    portunus = Portunus()
    portunus.cleanup_info({})


def test_main():

    class MockPortunus(Portunus):

        @staticmethod
        def execute_command(command, message, change_dir=None, failok=False, shell=False):
            return 0

        @staticmethod
        def execute_prompt(questions):
            return {'network_exist': False, 'gauge_1': True, 'network_name_1': 'foo', 'faucet_ip_1': '192.168.1.1', 'network_mode_1': 'nat', 'network_options': {'Specify Subnet': True}, 'faucet_port_1': '6653', 'gauge_ip_1': '192.168.1.1', 'gauge_port_1': '6654', 'intro': {'start containers': True}, 'num_networks': 2, 'num_containers_1': 1, 'container_image_1': 'foo', 'network_name_2': 'foo', 'network_mode_2': 'flat', 'faucet_ip_2': '192.168.2.1', 'faucet_port_2': '6653', 'gauge_2': False, 'num_containers_2': 0}

    mock_portunus = MockPortunus()
    mock_portunus.main()
