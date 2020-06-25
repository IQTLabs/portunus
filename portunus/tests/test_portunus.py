# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import textwrap

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
