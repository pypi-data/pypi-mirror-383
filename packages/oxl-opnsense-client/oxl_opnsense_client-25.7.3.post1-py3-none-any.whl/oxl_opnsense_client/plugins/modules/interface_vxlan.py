#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/interfaces.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.interface_vxlan import Vxlan

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/interface.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/interface.html'


def run_module(module_input):
    module_args = dict(
        # device_id=dict(type='str', required=True),  # can't be configured
        interface=dict(type='str', required=False, aliases=['vxlandev', 'device', 'int']),
        id=dict(type='int', required=True, aliases=['vxlanid', 'vni']),
        local=dict(
            type='str', required=False, aliases=[
                'source_address', 'source_ip', 'vxlanlocal', 'source', 'src',
            ],
            description='The source address used in the encapsulating IPv4/IPv6 header. The address should '
                        'already be assigned to an existing interface. When the interface is configured in '
                        'unicast mode, the listening socket is bound to this address.'
        ),
        local_port=dict(
            type='int', required=False, aliases=[
                'source_port', 'vxlanlocalport', 'srcport',
            ],
            description='Define the port to be used.'
        ),
        remote=dict(
            type='str', required=False, aliases=[
                'remote_address', 'remote_ip', 'destination', 'vxlanremote', 'dest',
            ],
            description='The interface can be configured in a unicast, or point-to-point, mode to create '
                        'a tunnel between two hosts. This is the IP address of the remote end of the tunnel.'
        ),
        remote_port=dict(
            type='int', required=False, aliases=[
                'destination_port', 'vxlanremoteport', 'destport',
            ],
            description='Define the port to be used.'
        ),
        group=dict(
            type='str', required=False, aliases=[
                'multicast_group', 'multicast_address', 'multicast_ip', 'vxlangroup',
            ],
            description='The interface can be configured in a multicast mode to create a virtual '
                        'network of hosts. This is the IP multicast group address the interface will join.'
        ),
        **RELOAD_MOD_ARG,
        **STATE_ONLY_MOD_ARG,
        **OPN_MOD_ARGS,
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        }
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    module_wrapper(Vxlan(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
