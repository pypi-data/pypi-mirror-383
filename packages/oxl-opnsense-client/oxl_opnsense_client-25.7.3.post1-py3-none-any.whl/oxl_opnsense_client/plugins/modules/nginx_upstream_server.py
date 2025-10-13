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
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG_DEF_FALSE
    from plugins.module_utils.main.nginx_upstream_server import UpstreamServer

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/nginx.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/nginx.html'


def run_module(module_input):
    module_args = dict(
        description=dict(type='str', alias=['name'], required=True, aliases=['name']),
        server=dict(type='str', required=False),
        port=dict(type='int', required=False),
        priority=dict(type='int', required=False),
        max_conns=dict(type='int', required=False),
        max_fails=dict(type='int', required=False),
        fail_timeout=dict(type='int', required=False),
        no_use=dict(
            type='str', required=False, choices=['', 'down', 'backup'], default='',
        ),
        **RELOAD_MOD_ARG_DEF_FALSE,
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


    module_wrapper(UpstreamServer(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
