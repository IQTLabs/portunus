import copy

import yaml

from portunus.config.faucet import FaucetConfig


def test_faucet_config():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    assert a.conf == {'tests/sample_faucet_config.yaml': {'vlans': {'office': {'vid': 100}}, 'include': ['sample_acls.yaml'], 'dps': {'t1-1': {'arp_neighbor_timeout': 900, 'timeout': 1801, 'dp_id': 1, 'hardware': 'Open vSwitch', 'stack': {'priority': 1}, 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 1}}, 2: {'output_only': True, 'mirror': [3]}, 3: {'native_vlan': 'office', 'loop_protect_external': True}}}, 't1-2': {'dp_id': 2, 'hardware': 'Open vSwitch', 'interface_ranges': {'4-10': {'native_vlan': 'office'}}, 'stack': {'priority': 2}, 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 2}}, 2: {'native_vlan': 'office'}, 3: {
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
    conf_changes = {'file': {'s2': 'bogus'}}
    a = FaucetConfig()
    conf_dict = yaml.safe_load(conf_str)
    a.conf = copy.deepcopy(conf_dict)
    a.set_config_section('dps', conf_changes)
    conf_dict['file']['dps'].update(conf_changes['file'])
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
    a = FaucetConfig()
    conf_dict = yaml.safe_load(conf_str)
    a.conf = copy.deepcopy(conf_dict)
    a.set_config_option('dps', 's1', conf_changes)
    conf_dict['file']['dps']['s1'].update(conf_changes)
    assert a.conf == conf_dict


def test_get_config_sections():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    sections = a.get_config_sections()
    assert sections == ['acls', 'dps', 'include', 'vlans']


def test_get_config_section():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    vlans = a.get_config_section('vlans')
    assert vlans == {
        'tests/sample_faucet_config.yaml': {'office': {'vid': 100}}}


def test_get_config_option():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    dp = a.get_config_option('dps', 't1-1')
    assert dp == {'arp_neighbor_timeout': 900, 'dp_id': 1, 'hardware': 'Open vSwitch', 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 1}},
                                                                                                      2: {'mirror': [3], 'output_only': True}, 3: {'loop_protect_external': True, 'native_vlan': 'office'}}, 'stack': {'priority': 1}, 'timeout': 1801}


def test_update_dps():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_dps(updates)
    conf_dict['tests/sample_faucet_config.yaml']['dps'].update(updates)
    assert a.conf == conf_dict


def test_update_dp():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_dp('t1-1', updates)
    conf_dict['tests/sample_faucet_config.yaml']['dps']['t1-1'].update(updates)
    assert a.conf == conf_dict


def test_del_dp():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    a.del_dp('t1-1')
    del conf_dict['tests/sample_faucet_config.yaml']['dps']['t1-1']
    assert a.conf == conf_dict


def test_update_interfaces():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_interfaces('t1-1', updates)
    conf_dict['tests/sample_faucet_config.yaml']['dps']['t1-1']['interfaces'].update(
        updates)
    assert a.conf == conf_dict


def test_update_interface_ranges():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_interface_ranges('t1-2', updates)
    conf_dict['tests/sample_faucet_config.yaml']['dps']['t1-2']['interface_ranges'].update(
        updates)
    assert a.conf == conf_dict


def test_del_interface():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    a.del_interface('t1-1', 1)
    del conf_dict['tests/sample_faucet_config.yaml']['dps']['t1-1']['interfaces'][1]
    assert a.conf == conf_dict


def test_update_interface():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_interface('t1-1', 1, updates)
    conf_dict['tests/sample_faucet_config.yaml']['dps']['t1-1']['interfaces'][1] = updates
    assert a.conf == conf_dict


def test_update_vlans():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_vlans(updates)
    conf_dict['tests/sample_faucet_config.yaml']['vlans'].update(updates)
    assert a.conf == conf_dict


def test_del_vlan():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    a.del_vlan('office')
    del conf_dict['tests/sample_faucet_config.yaml']['vlans']['office']
    assert a.conf == conf_dict


def test_update_vlan():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_vlan('office', updates)
    conf_dict['tests/sample_faucet_config.yaml']['vlans']['office'] = updates
    assert a.conf == conf_dict


def test_update_acls():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_acls(updates)
    conf_dict['tests/sample_faucet_config.yaml']['acls'].update(updates)
    # TODO test fails because the function we're testing is doing the wrong thing for multi-file defined acls
    #assert a.conf == conf_dict


def test_del_acl():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    a.del_acl('acl_same_a')
    del conf_dict['tests/sample_acls.yaml']['acls']['acl_same_a']
    assert a.conf == conf_dict


def test_update_acl():
    a = FaucetConfig(path='tests/sample_faucet_config.yaml')
    conf_dict = copy.deepcopy(a.conf)
    updates = {'new_key': 'foo', 'sw2': 'no more switch'}
    a.update_acl('acl_diff_d', updates)
    conf_dict['tests/sample_faucet_config.yaml']['acls']['acl_diff_d'] = updates
    print(a.conf)
    print(conf_dict)
    assert a.conf == conf_dict
