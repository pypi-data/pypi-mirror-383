#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, RELOAD_MOD_ARG, STATE_MOD_ARG
    from plugins.module_utils.main.webproxy_remote_acl import Acl

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'


def run_module(module_input):
    module_args = dict(
        file=dict(
            type='str', required=True, aliases=['filename'],
            description='Unique file-name to store the remote acl in'
        ),
        url=dict(
            type='str', required=False,
            description='Url to fetch the acl from'
        ),
        username=dict(
            type='str', required=False, aliases=['user'],
            description='Optional user for authentication'
        ),
        password=dict(
            type='str', required=False, aliases=['pwd'],
            description='Optional password for authentication',
            no_log=True,
        ),
        categories=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['cat', 'filter'],
            description='Select categories to use, leave empty for all. '
                        'Categories are visible in the WEB-UI after initial download'
        ),
        verify_ssl=dict(
            type='bool', required=False, default=True, aliases=['verify'],
            description='If certificate validation should be done - relevant if '
                        'self-signed certificates are used on the target server!'
        ),
        description=dict(
            type='str', required=False, aliases=['desc'],
            description='A description to explain what this blacklist is intended for'
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

    module_wrapper(Acl(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
