from portunus.config.faucet import FaucetConfig


def test_faucet_config():
    a = FaucetConfig('tests/sample_faucet_config.yaml')
    assert a.conf == {'tests/sample_faucet_config.yaml': {'vlans': {'office': {'vid': 100}}, 'include': ['sample_acls.yaml'], 'dps': {'t1-1': {'arp_neighbor_timeout': 900, 'timeout': 1801, 'dp_id': 1, 'hardware': 'Open vSwitch', 'stack': {'priority': 1}, 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 1}}, 2: {'output_only': True, 'mirror': [3]}, 3: {'native_vlan': 'office', 'loop_protect_external': True}}}, 't1-2': {'dp_id': 2, 'hardware': 'Open vSwitch', 'stack': {'priority': 2}, 'interfaces': {1: {'stack': {'dp': 't2-1', 'port': 2}}, 2: {'native_vlan': 'office'}, 3: {
        'native_vlan': 'office', 'loop_protect_external': True}}}, 't2-1': {'dp_id': 3, 'hardware': 'Open vSwitch', 'interfaces': {1: {'stack': {'dp': 't1-1', 'port': 1}}, 2: {'stack': {'dp': 't1-2', 'port': 1}}, 3: {'native_vlan': 'office', 'loop_protect_external': False}}}}, 'acls': {'acl_diff_d': [{'rule': {'actions': {'allow': 0}}}]}}, 'tests/sample_acls.yaml': {'include': ['notafile.yaml'], 'acls': {'acl_same_a': [{'rule': {'actions': {'allow': 1}}}], 'acl_same_b': [{'rule': {'actions': {'allow': 1}}}], 'acl_diff_c': [{'rule': {'actions': {'allow': 0}}}]}}}
