import yaml


class FaucetConfig():

    def __init__(self, path):
        self.conf = self.get_config(path)

    @staticmethod
    def get_config(path):
        conf = {}
        with open(path) as f:
            conf[path] = yaml.load(f, Loader=yaml.FullLoader)
        if 'include' in conf[path]:
            for include in conf[path]['include']:
                conf.update(FaucetConfig.get_config(include))
        return conf

    @staticmethod
    def save_config(conf):
        for path in conf:
            with open(path, 'w') as f:
                yaml.dump(conf[path], f)

    def set_config_section(self, section, changes):
        for f in self.conf.keys():
            if section in self.conf[f]:
                self.conf[f][section].update(changes)

    def set_config_option(self, section, option, changes, tier=None):
        for f in self.conf.keys():
            if tier and tier in self.conf[f]:
                if section in self.conf[f][tier]:
                    if option in self.conf[f][tier][section]:
                        self.conf[f][tier][section][option].update(changes)
            else:
                if section in self.conf[f]:
                    if option in self.conf[f][section]:
                        self.conf[f][section][option].update(changes)

    def get_config_sections(self):
        sections = []
        for f in self.conf.keys():
            for key in self.conf[f].keys():
                sections.append(key)
        return sections

    def get_config_section(self, section, tier=None):
        for f in self.conf.keys():
            if tier and tier in self.conf[f]:
                if section in self.conf[f][tier]:
                    return self.conf[f][tier][section]
            else:
                if section in self.conf[f]:
                    return self.conf[f][section]
        return {}

    def get_config_option(self, section, option, tier=None):
        section = self.get_config_section(section, tier=tier)
        if option in section:
            return section[option]
        return {}

    def update_dps(self, updates):
        dps = self.get_config_section('dps')
        dps.update(updates)
        self.set_config_section('dps', dps)

    def update_dp(self, dp, updates):
        switch = self.get_config_option('dps', dp)
        switch.update(updates)
        self.set_config_option('dps', dp, switch)

    def del_dp(self, dp_name):
        dps = self.get_config_section('dps')
        if dp_name in dps:
            del dps[dp_name]
        self.set_config_section('dps', dps)

    def update_interfaces(self, dp, updates):
        interfaces = self.get_config_option(dp, 'interfaces', tier='dps')
        interfaces.update(updates)
        self.set_config_option(dp, 'interfaces', interfaces, tier='dps')

    def update_interface_ranges(self, dp, updates):
        interface_ranges = self.get_config_option(
            dp, 'interface_ranges', tier='dps')
        interface_ranges.update(updates)
        self.set_config_option(dp, 'interface_ranges',
                               interface_ranges, tier='dps')

    def del_interface(self, dp, interface_num):
        interfaces = self.get_config_option(dp, 'interfaces', tier='dps')
        if interface_num in interfaces:
            del interfaces[interface_num]
        self.set_config_option(dp, 'interfaces', interfaces, tier='dps')

    def update_interface(self, dp, interface, updates):
        interfaces = self.get_config_option(dp, 'interfaces', tier='dps')
        interfaces[interface] = updates
        self.set_config_option(dp, 'interfaces', interfaces, tier='dps')

    def update_vlans(self, updates):
        vlans = self.get_config_section('vlans')
        vlans.update(updates)
        self.set_config_section('vlans', vlans)

    def del_vlan(self, vlan):
        vlans = self.get_config_section('vlans')
        if vlan in vlans:
            del vlans[vlan]
        self.set_config_section('vlans', vlans)

    def update_vlan(self, vlan, updates):
        vlans = self.get_config_section('vlans')
        vlans[vlan] = updates
        self.set_config_section('vlans', vlans)

    def update_acls(self, updates):
        acls = self.get_config_section('acls')
        acls.update(updates)
        self.set_config_section('acls', acls)

    def del_acl(self, acl):
        acls = self.get_config_section('acls')
        if acl in acls:
            del acls[acl]
        self.set_config_section('acls', acls)

    def update_acl(self, acl, updates):
        acls = self.get_config_section('acls')
        acls[acl] = updates
        self.set_config_section('acls', acls)

    def add_rule(self, acl, rule):
        rules = self.get_config_option('acls', acl)
        rules.append(rule)
        self.set_config_option('acls', acl, rules)

    def update_rules(self, acl, updates):
        self.set_config_option('acls', acl, updates)


#################
# EXAMPLE USAGE #
#################

f = FaucetConfig('faucet.yaml')
print(f.conf)
updates = {'new_key': 'foo', 'sw2': 'no more switch'}
f.update_dps(updates)
f.update_dp('sw1', updates)
print(f.conf)
print(f.get_config_sections())
print(f.get_config_section('routers'))
print(f.get_config_option('dps', 'sw1'))
print(f.get_config_option('acls', 'access-port-protect'))
f.del_dp('sw2')
print(f.conf)
f.update_interfaces('sw1', updates)
print(f.conf)
