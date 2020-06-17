import os

import yaml


# TODO
# deal with removing the last one of something
# deal with adding the first one of something

class FaucetConfig():

    # TODO add params needed to do RPC
    def __init__(self, path=None, local=True):
        if local:
            self.conf = self.read_config(path)
        else:
            self.conf = self.get_config()

    @staticmethod
    def get_config():
        conf = {}
        # TODO
        return conf

    @staticmethod
    def send_config():
        # TODO
        pass

    @staticmethod
    def read_config(path):
        conf = {}
        if not path:
            return conf
        dirname = os.path.dirname(path)
        try:
            with open(path) as f:
                conf[path] = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            return conf
        if 'include' in conf[path]:
            for include in conf[path]['include']:
                conf.update(FaucetConfig.read_config(
                    os.path.join(dirname, include)))
        return conf

    @staticmethod
    def save_config(conf):
        for path in conf:
            with open(path, 'w') as f:
                yaml.dump(conf[path], f)

    def set_config_section(self, section, changes):
        for f in self.conf.keys():
            if section in self.conf[f]:
                self.conf[f][section].update(changes[f])
                return

    def set_config_option(self, section, option, changes, tier=None):
        for f in self.conf.keys():
            if tier and tier in self.conf[f]:
                if section in self.conf[f][tier]:
                    if option in self.conf[f][tier][section]:
                        self.conf[f][tier][section][option].update(changes)
                        return
            else:
                if section in self.conf[f]:
                    if option in self.conf[f][section]:
                        self.conf[f][section][option].update(changes)
                        return

    def get_config_sections(self):
        sections = []
        for f in self.conf.keys():
            for key in self.conf[f].keys():
                sections.append(key)
        return sorted(list(set(sections)))

    def get_config_section(self, section, tier=None):
        section_dict = {}
        for f in self.conf.keys():
            if tier and tier in self.conf[f]:
                if section in self.conf[f][tier]:
                    section_dict[f] = self.conf[f][tier][section]
            else:
                if section in self.conf[f]:
                    section_dict[f] = self.conf[f][section]
        return section_dict

    def get_config_option(self, section, option, tier=None):
        section = self.get_config_section(section, tier=tier)
        for f in section:
            if option in section[f]:
                return section[f][option]
        return {}

    def update_dps(self, updates):
        dps = self.get_config_section('dps')
        for f in dps:
            dps[f].update(updates)
        self.set_config_section('dps', dps)

    def update_dp(self, dp, updates):
        switch = self.get_config_option('dps', dp)
        switch.update(updates)
        self.set_config_option('dps', dp, switch)

    def del_dp(self, dp_name):
        dps = self.get_config_section('dps')
        for f in dps:
            if dp_name in dps[f]:
                del dps[f][dp_name]
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
        for f in vlans:
            vlans[f].update(updates)
        self.set_config_section('vlans', vlans)

    def del_vlan(self, vlan):
        vlans = self.get_config_section('vlans')
        for f in vlans:
            if vlan in vlans[f]:
                del vlans[f][vlan]
        self.set_config_section('vlans', vlans)

    def update_vlan(self, vlan, updates):
        vlans = self.get_config_section('vlans')
        for f in vlans:
            vlans[f][vlan] = updates
        self.set_config_section('vlans', vlans)

    def update_acls(self, updates):
        acls = self.get_config_section('acls')
        for f in acls:
            # TODO this probably needs to go another level deeper to only update acls that changed that exist in each file, not update to all files
            acls[f].update(updates)
        self.set_config_section('acls', acls)

    def del_acl(self, acl):
        acls = self.get_config_section('acls')
        for f in acls:
            if acl in acls[f]:
                del acls[f][acl]
        self.set_config_section('acls', acls)

    def update_acl(self, acl, updates):
        acls = self.get_config_section('acls')
        for f in acls:
            if acl in acls[f]:
                acls[f][acl] = updates
        self.set_config_section('acls', acls)

    def add_rule(self, acl, rule):
        rules = self.get_config_option('acls', acl)
        rules.append(rule)
        self.set_config_option('acls', acl, rules)

    def update_rules(self, acl, updates):
        self.set_config_option('acls', acl, updates)
