# v0.2.3 (2020-10-23)

- Validates NIC selection for adding to networks
- Only add volume options when starting >0 containers
- Use graph_dovesnap from pip package
- Use latest released version of dovesnap when installing
- Implemented option to cleanup dovesnap and ovs containers
- Updated codecov, faucetconfrpc, ptyprocess

# v0.2.2 (2020-10-09)

- Fix github key retry handling
- Add option to provide volume to containers
- Update faucetconfrpc, pytest

# v0.2.1 (2020-09-04)

- Show OF controllers in graphviz
- Check if ACLs are empty
- Updated faucetconfrpc

# v0.2.0 (2020-08-31)

- Initial offering. Supports creating/deleting VMs and/or containers attached to OVS and wired to Faucet/Gauge.
- Leverages Dovesnap, Open vSwitch, libvirt/kvm, Docker, and FaucetConfRPC among other things to accomplish easy management of containers and VMs in both virtual and hardware environments controlled by SDN.
