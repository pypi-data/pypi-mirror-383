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
    from plugins.module_utils.main.interface_vlan import Vlan

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/interface.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/interface.html'


def run_module(module_input):
    module_args = dict(
        device=dict(
            type='str', required=False, aliases=['vlanif'],
            description="Optional 'device' of the entry. Needs to start with 'vlan0'",
        ),
        interface=dict(
            type='str', required=False, aliases=['parent', 'port', 'int', 'if'],
            description='Existing VLAN capable interface - you must provide the network '
                        "port as shown in 'Interfaces - Assignments - Network port'"
        ),
        vlan=dict(
            type='int', required=False, aliases=['tag', 'id'],
            description='802.1Q VLAN tag (between 1 and 4094)'
        ),
        priority=dict(
            type='int', required=False, default=0, aliases=['prio', 'pcp'],
            description='802.1Q VLAN PCP (priority code point)'
        ),
        description=dict(type='str', required=True, aliases=['desc', 'name']),
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

    module_wrapper(Vlan(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
