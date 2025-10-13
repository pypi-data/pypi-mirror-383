#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/dnsmasq.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG
    from plugins.module_utils.main.dnsmasq_boot import Boot

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/dnsmasq.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/dnsmasq.html'


def run_module(module_input):
    module_args = dict(
        description=dict(
            type='str', required=True, aliases=['desc'],
            description='DHCP boot description.',
        ),
        interface=dict(
            type='str', required=False, aliases=['int'],
            description='Interface this boot options is set for.',
        ),
        tag=dict(
            type='list', elements='str', required=False, default=[], aliases=['t'],
            description='DHCP boot option is only sent when all the tags are matched.',
        ),
        filename=dict(
            type='str', required=False, aliases=['file', 'f'],
            description='DHCP boot file path.',
        ),
        servername=dict(
            type='str', required=False,
            description='DHCP boot server name.',
        ),
        address=dict(
            type='str', required=False,
            description='DHCP boot server address.',
        ),
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
        required_if=[
            ('state', 'present', ('filename',)),
        ]
    )

    module_wrapper(Boot(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
