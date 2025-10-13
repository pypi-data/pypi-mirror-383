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
    from plugins.module_utils.main.postfix_headercheck import Headercheck

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/postfix.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/postfix.html'


def run_module(module_input):
    module_args = dict(
        expression=dict(
            type='str', required=True,
            description='Set a regexp (POSIX regular expression) and an action to process like '
                        '\'/^\\s*User-Agent/ IGNORE\'.',
        ),
        filter=dict(
            type='str', required=True, choices=['WHILE_DELIVERING', 'WHILE_RECEIVING'],
            description='Set when the header_check should be processed. One of: WHILE_DELIVERING or WHILE_RECEIVING.',
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

    module_wrapper(Headercheck(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
