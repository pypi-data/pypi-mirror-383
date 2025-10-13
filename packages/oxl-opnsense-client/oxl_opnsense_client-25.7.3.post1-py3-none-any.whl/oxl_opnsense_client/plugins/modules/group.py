#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/auth.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG
    from plugins.module_utils.main.group import Group

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/auth.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/auth.html'


def run_module(module_input):
    module_args = dict(
        name=dict(
            type='str', required=True, aliases=['n'],
            description='Group name',
        ),
        description=dict(type='str', required=False, aliases=['desc']),
        member=dict(
            type='list', required=False, aliases=['m'], elements='str',
            default=[],
        ),
        privilege=dict(
            type='list', required=False, aliases=['priv', 'p'], elements='str',
            default=[],
        ),
        source_net=dict(
            type='list', required=False, aliases=['source', 'src', 's'], elements='str', default=[],
            description='List of networks which constraint the membership of this group to their location.',
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
    )

    module_wrapper(Group(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
