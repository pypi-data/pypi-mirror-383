#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/quagga.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.frr_ospf3_interface import Interface

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_ospf.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_ospf.html'


def run_module(module_input):
    module_args = dict(
        interface=dict(type='str', required=True, aliases=['name', 'int']),
        area=dict(
            type='str', required=False,
            description='Area in wildcard mask style like 0.0.0.0 and no decimal 0'
        ),
        passive=dict(type='bool', required=False, default=False),
        cost=dict(type='int', required=False),
        cost_demoted=dict(type='int', required=False, default=65535),
        carp_depend_on=dict(
            type='str', required=False,
            description='The carp VHID to depend on, when this virtual address is not in '
                        'master state, the interface cost will be set to the demoted cost'
        ),
        hello_interval=dict(type='int', required=False, aliases=['hello']),
        dead_interval=dict(type='int', required=False, aliases=['dead']),
        retransmit_interval=dict(type='int', required=False, aliases=['retransmit']),
        transmit_delay=dict(type='int', required=False, aliases=['delay']),
        priority=dict(type='int', required=False, aliases=['prio']),
        network_type=dict(
            type='str', required=False, aliases=['nw_type'],
            choices=['broadcast', 'point-to-point'],
        ),
        match_fields=dict(
            type='list', required=False, elements='str',
            description='Fields that are used to match configured interface with the running config - '
                        "if any of those fields are changed, the module will think it's a new entry",
            choices=['interface', 'area', 'passive', 'carp_depend_on', 'network_type'],
            default=['interface', 'area'],
        ),
        **RELOAD_MOD_ARG,
        **STATE_MOD_ARG,
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

    module_wrapper(Interface(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
