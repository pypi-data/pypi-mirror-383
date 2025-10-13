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
    from plugins.module_utils.main.unbound_host import Host

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/unbound_host.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/unbound_host.html'


def run_module(module_input):
    module_args = dict(
        hostname=dict(type='str', required=True, aliases=['host', 'h']),
        domain=dict(type='str', required=True, aliases=['dom', 'd']),
        record_type=dict(
            type='str', required=False, aliases=['type', 'rr', 'rt'],
            choices=['A', 'AAAA', 'MX'], default='A',
        ),
        value=dict(type='str', required=False, aliases=['server', 'srv', 'mx']),
        prio=dict(
            type='int', required=False, aliases=['mxprio'], default=10,
            description='Priority that is only used for MX record types'
        ),
        description=dict(type='str', required=False, aliases=['desc']),
        match_fields=dict(
            type='list', required=False, elements='str',
            description='Fields that are used to match configured host-overrides with the running config - '
                        "if any of those fields are changed, the module will think it's a new entry",
            choices=[
                'hostname', 'domain', 'record_type', 'value',
                'prio', 'description'
            ],
            default=['hostname', 'domain', 'record_type', 'value', 'prio'],
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

    module_wrapper(Host(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
