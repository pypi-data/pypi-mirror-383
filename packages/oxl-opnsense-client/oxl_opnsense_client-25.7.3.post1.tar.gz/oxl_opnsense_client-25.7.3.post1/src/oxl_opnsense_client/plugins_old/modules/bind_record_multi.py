#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2024, AnsibleGuy <guy@ansibleguy.net>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/bind.html

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ansibleguy.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.utils import profiler
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.helper.main import \
        diff_remove_empty
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.defaults.main import \
        STATE_MOD_ARG, RELOAD_MOD_ARG, INFO_MOD_ARG, FAIL_MOD_ARG_MULTI
    from ansible_collections.ansibleguy.opnsense.plugins.module_utils.main.bind_record_multi import \
        process

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://opnsense.ansibleguy.net/en/latest/modules/bind.html'
# EXAMPLES = 'https://opnsense.ansibleguy.net/en/latest/modules/bind.html'


def run_module():
    module_args = dict(
        records=dict(type='dict', required=True),
        match_fields=dict(
            type='list', required=False, elements='str',
            description='Fields that are used to match configured records with the running config - '
                        "if any of those fields are changed, the module will think it's a new entry",
            choices=['domain', 'name', 'type', 'value'],
            default=['domain', 'name', 'type'],
        ),
        **FAIL_MOD_ARG_MULTI,
        **STATE_MOD_ARG,
        **INFO_MOD_ARG,
        **RELOAD_MOD_ARG,
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        }
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.params['profiling'] or module.params['debug']:
        profiler(
            check=process,
            kwargs=dict(
                m=module, p=module.params, r=result,
            ),
        )

    else:
        process(m=module, p=module.params, r=result)

    result['diff'] = diff_remove_empty(result['diff'])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
