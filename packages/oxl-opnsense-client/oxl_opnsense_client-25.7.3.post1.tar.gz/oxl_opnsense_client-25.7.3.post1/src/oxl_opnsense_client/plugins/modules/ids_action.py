#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/ids.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS
    from plugins.module_utils.base.api import \
        single_get, single_post

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/ids.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/ids.html'

ACTION_MAPPING = {
    'get_alert_info': {'a': 'getAlertInfo', 'post': False},
    'get_alert_logs': {'a': 'getAlertLogs', 'post': False},
    'query_alerts': {'a': 'queryAlerts', 'post': False},
    'status': {'post': False},
    'reconfigure': {'post': True},
    'restart': {'post': True},
    'start': {'post': True},
    'stop': {'post': True},
    'drop_alert_log': {'a': 'dropAlertLog', 'post': True},
    'reload_rules': {'a': 'reloadRules', 'post': True},
    'update_rules': {'a': 'updateRules', 'post': True},
}

def run_module(module_input):
    module_args = dict(
        action=dict(
            type='str', required=True, aliases=['do', 'a'],
            choices=[
                'get_alert_logs', 'query_alerts', 'get_alert_info', 'status',
                'reconfigure', 'restart', 'start', 'stop',
                'drop_alert_log', 'reload_rules', 'update_rules',
            ],
        ),
        alert_id=dict(
            type='str', required=False, aliases=['alert'],
            description="Parameter Alert-ID needed for 'get_alert_info'",
        ),
        **OPN_MOD_ARGS,
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    action = module.params['action']
    if action == 'get_alert_info' and module.params['alert_id'] is None:
        module.fail_json("You need to provide an Alert-ID as 'alert_id' to execute 'get_alert_info'!")

    # translate actions to api-commands
    cmd = action
    if 'a' in ACTION_MAPPING[action]:
        cmd = ACTION_MAPPING[action]['a']

    result['executed'] = cmd

    # execute action or pull status
    if ACTION_MAPPING[action]['post']:
        result['changed'] = True

        if not module.check_mode:
            single_post(
                module=module,
                cnf={
                    'module': 'ids',
                    'controller': 'service',
                    'command': cmd,
                }
            )

    else:
        params = []
        if module.params['alert_id'] is not None:
            params = [module.params['alert_id']]

        info = single_get(
            module=module,
            cnf={
                'module': 'ids',
                'controller': 'service',
                'command': cmd,
                'params': params,
            }
        )

        if 'response' in info:
            info = info['response']

            if isinstance(info, str):
                info = info.strip()

        result['data'] = info

    return result






if __name__ == '__main__':
    pass
