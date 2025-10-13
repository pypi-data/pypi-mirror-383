#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/firewall.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import \
        module_wrapper, is_multi_module_call, module_multi_wrapper
    from plugins.module_utils.base.multi import \
        build_multi_mod_args, MultiModuleCallbacks
    from plugins.module_utils.defaults.main import \
        RELOAD_MOD_ARG_DEF_FALSE, OPN_MOD_ARGS, STATE_MOD_ARG
    from plugins.module_utils.main.alias import Alias
    from plugins.module_utils.helper.main import ensure_list
    from plugins.module_utils.helper.alias import \
        builtin_alias, build_updatefreq

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/alias.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/alias.html'


class MultiCallbacks(MultiModuleCallbacks):
    @staticmethod
    def build(entry: dict) -> dict:
        entry['content'] = list(map(str, ensure_list(entry['content'])))
        if 'updatefreq_days' in entry:
            entry['updatefreq_days'] = build_updatefreq(entry['updatefreq_days'])

        return entry

    @staticmethod
    def purge_exclude(entry: dict) -> bool:
        return builtin_alias(entry['name'])


def run_module(module_input):
    entry_args = dict(
        name=dict(type='str', required=True, aliases=['n']),
        description=dict(
            type='str', required=False, default='', aliases=['desc'],
        ),
        content=dict(
            type='list', required=False, default=[], aliases=['c', 'cont'], elements='str',
        ),
        type=dict(type='str', required=False, default='host', aliases=['t'], choices=[
            'host', 'network', 'port', 'url', 'urltable', 'geoip', 'networkgroup',
            'mac', 'dynipv6host', 'internal', 'external',
        ]),
        updatefreq_days=dict(
            type='str', default='', required=False,
            description="Update frequency used by type 'urltable' in days - per example '0.5' for 12 hours"
        ),
        interface=dict(
            type='str', default=None, aliases=['int', 'if'], required=False,
            description=' Select the interface for the V6 dynamic IP.',
        ),
        path_expression=dict(
            type='str', default='', aliases=['pe', 'jq'], required=False,
            description='Simplified expression to select a field inside a container, a dot is used as field separator. '
                        'Expressions using the jq language are also supported.',
        ),
        **STATE_MOD_ARG,
    )
    entry_multi_args = build_multi_mod_args(
        mod_args=entry_args,
        aliases=['aliases'],
        not_required=['name'],
    )

    module_args = dict(
        **RELOAD_MOD_ARG_DEF_FALSE,  # default-true takes pretty long sometimes (urltables and so on)
        **entry_args,
        **entry_multi_args,
        **OPN_MOD_ARGS,
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ('name', 'multi'), ('name', 'multi_purge'), ('name', 'multi_control.purge_all')
        ],
        required_one_of=[
            ('name', 'multi', 'multi_purge', 'multi_control.purge_all'),
        ],
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        }
    )

    if is_multi_module_call(module):
        module_multi_wrapper(
            module=module,
            result=result,
            obj=Alias,
            kind='alias',
            entry_args=entry_multi_args,
            callbacks=MultiCallbacks(),
        )

    else:
        module_wrapper(Alias(module=module, result=result))

    return result






if __name__ == '__main__':
    pass
