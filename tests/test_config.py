import yaml

from portunus.config.faucet import FaucetConfig


def test_faucet_config():
    a = FaucetConfig('tests/sample_faucet_config.yaml')
    assert a.conf == {'tests/sample_faucet_config.yaml': {'vlans': {'office': {'vid': 100}}, 'include': ['sample_acls.yaml'], 'dps': {'t1-1': {'arp_neighbor_timeout': 900, 'timeout': 1801, 'dp_id': 1, 'hardware': 'Open vSwitch', 'stack': {'priority': 1}, 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 1}}, 2: {'output_only': True, 'mirror': [3]}, 3: {'native_vlan': 'office', 'loop_protect_external': True}}}, 't1-2': {'dp_id': 2, 'hardware': 'Open vSwitch', 'stack': {'priority': 2}, 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 2}}, 2: {'native_vlan': 'office'}, 3: {
        'native_vlan': 'office', 'loop_protect_external': True}}}, 't2-1': {'dp_id': 3, 'hardware': 'Open vSwitch', 'interfaces': {1: {'stack': {'dp': 't1-1', 'port': 1}}, 2: {'stack': {'dp': 't1-2', 'port': 1}}, 3: {'native_vlan': 'office', 'loop_protect_external': False}}}}, 'acls': {'acl_diff_d': [{'rule': {'actions': {'allow': 0}}}]}}, 'tests/sample_acls.yaml': {'include': ['notafile.yaml'], 'acls': {'acl_same_a': [{'rule': {'actions': {'allow': 1}}}], 'acl_same_b': [{'rule': {'actions': {'allow': 1}}}], 'acl_diff_c': [{'rule': {'actions': {'allow': 0}}}]}}}


def test_set_config_section():
    conf_str = """
file:
    dps:
        s1:
            interfaces:
                1:
                    output_only: true
                    mirror: [2]
                2:
                    native_vlan: 100
                3:
                    native_vlan: 100
"""
    conf_changes = {'s2': 'bogus'}
    a = FaucetConfig(None)
    conf_dict = yaml.safe_load(conf_str)
    a.conf = conf_dict
    a.set_config_section('dps', conf_changes)
    conf_dict['file'].update(conf_changes)
    assert a.conf == conf_dict


def test_set_config_option():
    conf_str = """
file:
    dps:
        s1:
            interfaces:
                1:
                    output_only: true
                    mirror: [2]
                2:
                    native_vlan: 100
                3:
                    native_vlan: 100
"""
    conf_changes = {'foo': 'bar'}
    a = FaucetConfig(None)
    conf_dict = yaml.safe_load(conf_str)
    a.conf = conf_dict
    a.set_config_option('dps', 's1', conf_changes)
    conf_dict['file']['dps']['s1'].update(conf_changes)
    assert a.conf == conf_dict


def test_get_config_sections():
    a = FaucetConfig('tests/sample_faucet_config.yaml')
    sections = a.get_config_sections()
    assert sections == ['acls', 'dps', 'include', 'vlans']


def test_get_config_section():
    a = FaucetConfig('tests/sample_faucet_config.yaml')
    vlans = a.get_config_section('vlans')
    assert vlans == {'office': {'vid': 100}}


def test_get_config_option():
    a = FaucetConfig('tests/sample_faucet_config.yaml')
    dp = a.get_config_option('dps', 't1-1')
    assert dp == {'arp_neighbor_timeout': 900, 'dp_id': 1, 'hardware': 'Open vSwitch', 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 1}},
                                                                                                      2: {'mirror': [3], 'output_only': True}, 3: {'loop_protect_external': True, 'native_vlan': 'office'}}, 'stack': {'priority': 1}, 'timeout': 1801}
