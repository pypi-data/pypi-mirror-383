#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/ipsec.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.main.ipsec_psk import PreSharedKey
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG_DEF_FALSE

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/ipsec.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/ipsec.html'


def run_module(module_input):
    module_args = dict(
        identity_local=dict(
            type='str', required=True, aliases=['identity', 'ident'],
            description='This can be either an IP address, fully qualified domain name or an email address.'
        ),
        identity_remote=dict(
            type='str', required=False, aliases=['remote_ident'],
            description='(optional) This can be either an IP address, fully qualified domain name or '
                        'an email address to identify the remote host.'
        ),
        psk=dict(type='str', required=False, no_log=True, aliases=['key', 'secret']),
        type=dict(
            type='str', required=False, choices=['PSK', 'EAP'], default='PSK', aliases=['kind'],
        ),
        match_fields=dict(
            type='list', required=False, elements='str',
            description='Fields that are used to match configured PSK with the running config - '
                        "if any of those fields are changed, the module will think it's a new entry",
            choices=['identity_local', 'identity_remote'],
            default=['identity_local'],
        ),
        **RELOAD_MOD_ARG_DEF_FALSE,
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

    module_wrapper(PreSharedKey(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
