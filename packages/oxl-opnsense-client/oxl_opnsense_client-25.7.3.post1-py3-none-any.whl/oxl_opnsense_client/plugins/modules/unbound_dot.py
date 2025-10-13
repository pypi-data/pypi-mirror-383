#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/unbound.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.unbound_dot import DnsOverTls

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/unbound_dot.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/unbound_dot.html'


def run_module(module_input):
    module_args = dict(
        domain=dict(
            type='str', required=False, aliases=['dom', 'd'],
            description='Provide a domain to limit the DNS-over-TLS to or leave empty to act as a catch-all'
        ),
        target=dict(
            type='str', required=True, aliases=['tgt', 'server', 'srv'],
            description='Server to forward the dns queries to'
        ),
        port=dict(
            type='int', required=False, default=53, aliases=['p'],
            description='DNS port of the target server'
        ),
        verify=dict(
            type='str', required=False, aliases=['common_name', 'cn', 'hostname'],
            description='Verify if CN in certificate matches this value, if not set - '
                        'certificate verification will not be performed!'
        ),
        type=dict(type='str', required=False, choices=['dot'], default='dot'),
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

    module_wrapper(DnsOverTls(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
