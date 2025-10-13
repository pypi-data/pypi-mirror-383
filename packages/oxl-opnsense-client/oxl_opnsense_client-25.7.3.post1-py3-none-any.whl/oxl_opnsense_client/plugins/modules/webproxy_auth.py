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
        OPN_MOD_ARGS, RELOAD_MOD_ARG
    from plugins.module_utils.main.webproxy_auth import General

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'


def run_module(module_input):
    module_args = dict(
        method=dict(
            type='str', required=False, aliases=['type', 'target'],
            description='The authentication backend to use - as shown in the '
                        "WEB-UI at 'System - Access - Servers'. Per example: "
                        "'Local Database'"
        ),
        group=dict(
            type='str', required=False, aliases=['local_group'],
            description='Restrict access to users in the selected (local)group. '
                        "NOTE: please be aware that users (or vouchers) which aren't "
                        "administered locally will be denied when using this option"
        ),
        prompt=dict(
            type='str', required=False, aliases=['realm'],
            default='OPNsense proxy authentication',
            description='The prompt will be displayed in the authentication request window'
        ),
        ttl_h=dict(
            type='int', required=False, default=2, aliases=['ttl', 'ttl_hours', 'credential_ttl'],
            description='This specifies for how long (in hours) the proxy server assumes '
                        'an externally validated username and password combination is valid '
                        '(Time To Live). When the TTL expires, the user will be prompted for '
                        'credentials again'
        ),
        processes=dict(
            type='int', required=False, default=5, aliases=['proc'],
            description='The total number of authenticator processes to spawn'
        ),
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

    module_wrapper(General(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
