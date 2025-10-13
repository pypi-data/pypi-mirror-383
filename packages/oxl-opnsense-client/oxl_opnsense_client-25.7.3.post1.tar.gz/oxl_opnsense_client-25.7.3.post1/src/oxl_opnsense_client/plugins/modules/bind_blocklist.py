#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/bind.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, EN_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.bind_blocklist import Blocklist

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/bind.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/bind.html'

BL_MAPPING = {
    'AdAway List': 'aa',
    'AdGuard List': 'ag',
    'Blocklist.site Ads': 'bla',
    'Blocklist.site Fraud': 'blf',
    'Blocklist.site Phishing': 'blp',
    'Cameleon List': 'ca',
    'Easy List': 'el',
    'EMD Malicious Domains List': 'emd',
    'Easyprivacy List': 'ep',
    'hpHosts Ads': 'hpa',
    'hpHosts FSA': 'hpf',
    'hpHosts PSH': 'hpp',
    'hpHosts PUP': 'hup',
    'Malwaredomain List': 'mw',
    'NoCoin List': 'nc',
    'PornTop1M List': 'pt',
    'Ransomware Tracker List': 'rw',
    'Simple Ad List': 'sa',
    'Simple Tracker List': 'st',
    'Steven Black List': 'sb',
    'WindowsSpyBlocker (spy)': 'ws',
    'WindowsSpyBlocker (update)': 'wsu',
    'WindowsSpyBlocker (extra)': 'wse',
    'YoYo List': 'yy',
}


def run_module(module_input):
    module_args = dict(
        block=dict(
            type='list', elements='str', required=False, choices=list(BL_MAPPING.keys()),
            aliases=['lists'], default=[],
            description="Blocklist's you want to enable"
        ),
        exclude=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['safe_list'],
            description='Domains to exclude from the filter'
        ),
        safe_google=dict(
            type='bool', required=False, default=False, aliases=['safe_search_google'],
        ),
        safe_duckduckgo=dict(
            type='bool', required=False, default=False, aliases=['safe_search_duckduckgo'],
        ),
        safe_youtube=dict(
            type='bool', required=False, default=False, aliases=['safe_search_youtube'],
        ),
        safe_bing=dict(
            type='bool', required=False, default=False, aliases=['safe_search_bing'],
        ),
        **EN_ONLY_MOD_ARG,
        **OPN_MOD_ARGS,
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
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    translated_lists = []
    for k in module.params['block']:
        translated_lists.append(BL_MAPPING[k])

    module.params['block'] = translated_lists

    module_wrapper(Blocklist(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
