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
    from plugins.module_utils.main.webproxy_pac_rule import Rule

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'


def run_module(module_input):
    module_args = dict(
        description=dict(
            type='str', required=True, aliases=['desc', 'name'],
            description='Unique description used to identify existing rules'
        ),
        matches=dict(
            type='list', elements='str', required=False, default=[],
            description='Matches you want to use in this rule. This matches '
                        'are joined using the selected separator',
        ),
        proxies=dict(
            type='list', elements='str', required=False, default=[],
            description='Proxies you want to use address using this rule',
        ),
        join_type=dict(
            type='str', required=False, default='and',
            aliases=['join'], choices=['and', 'or'],
            description="A separator to join the matches. 'or' means any match "
                        'can be true which can be used to configure the same '
                        "proxy for multiple networks while 'and' means all matches "
                        'must be true which can be used to assign the proxy in a '
                        'more detailed way',
        ),
        match_type=dict(
            type='str', required=False, default='if',
            aliases=['operator'], choices=['if', 'unless'],
            description="Choose 'if' in case any case you want to ensure a match to "
                        "evaluate as is, else choose 'unless' if you want the negated "
                        'version. Unless is used if you want to use the proxy for every '
                        'host but not for some special ones',
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

    module_wrapper(Rule(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
