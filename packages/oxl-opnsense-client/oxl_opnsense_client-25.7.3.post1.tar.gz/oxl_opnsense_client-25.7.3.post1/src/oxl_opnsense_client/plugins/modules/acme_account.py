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
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.acme_account import Account

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/en/latest/modules/acmeclient.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/en/latest/modules/acmeclient.html'


def run_module(module_input):
    module_args = dict(
        name=dict(
            type='str', required=True,
            description='Name to identify this account.',
        ),
        description=dict(
            type='str', required=False, aliases=['desc'],
            description='Description for this account.',
        ),
        email=dict(
            type='str', required=False,
            description='E-mail address for this account.',
        ),
        ca=dict(
            type='str', required=False, default='letsencrypt',
            choices=[
                'buypass', 'buypass_test', 'google', 'google_test', 'letsencrypt', 'letsencrypt_test', 'sslcom',
                'zerossl', 'custom',
            ],
        ),
        custom_ca=dict(
            type='str', required=False,
            description='The HTTPS URL of the custom ACME CA that should be used for this account and all associated '
                        'certificates. For example: https://ca.internal/acme/directory'
        ),
        eab_kid=dict(
            type='str', required=False,
            description='An value provided by the CA when using ACME External Account Binding (EAB).',
        ),
        eab_hmac=dict(
            type='str', required=False,
            description='An value provided by the CA when using ACME External Account Binding (EAB).',
        ),
        register=dict(
            type='bool', required=False, default=False,
            description='Register the selected account with the configured ACME CA',
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
        required_if=[
            ('ca', 'custom', ('custom_ca',)),
        ],
    )

    module_wrapper(Account(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
