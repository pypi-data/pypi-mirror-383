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
    from plugins.module_utils.main.frr_bgp_community_list import Community

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_bgp.html
#                  #oxlorg-opnsense-frr-bgp-community-list'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_bgp.html#id5'


def run_module(module_input):
    module_args = dict(
        description=dict(type='str', required=True, aliases=['desc']),
        number=dict(type='str', required=False, aliases=['nr']),
        seq=dict(type='int', required=False, aliases=['seq_number']),
        action=dict(type='str', required=False, options=['permit', 'deny']),
        community=dict(
            type='str', required=False, aliases=['comm'],
            description='The community you want to match. You can also regex and it is '
                        'not validated so please be careful.'
        ),
        **STATE_MOD_ARG,
        **RELOAD_MOD_ARG,
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

    module_wrapper(Community(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
