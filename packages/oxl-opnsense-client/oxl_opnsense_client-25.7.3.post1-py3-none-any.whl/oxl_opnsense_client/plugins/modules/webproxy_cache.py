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
    from plugins.module_utils.main.webproxy_cache import Cache

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'

BLANK_VALUES = {
    'memory_cache_mode': 'default',
}


def run_module(module_input):
    module_args = dict(
        memory_mb=dict(
            type='int', required=False, default=256, aliases=['memory', 'mem'],
            description='The cache memory size to use or zero to disable completely'
        ),
        size_mb=dict(
            type='int', required=False, default=100, aliases=['size'],
            description='The storage size for the local cache'
        ),
        directory=dict(
            type='str', required=False, default='/var/squid/cache', aliases=['dir'],
            description='The location for the local cache'
        ),
        slot_size=dict(
            type='int', required=False, default=16384,
            description='Defines the size of a database record used to store cached responses. '
                        'Value should be a multiple of the OS I/O page size.'
        ),
        swap_timeout=dict(
            type='int', required=False, default=0,
            description='Prevents Squid from reading/writing to disk if the operation exceeds the '
                        'specified timelimit in milliseconds.'
        ),
        max_swap_rate=dict(
            type='int', required=False, default=0, aliases=['swap_rate'],
            description='Limits disk access by setting a maximum I/O rate in swaps per second.'
        ),
        size_mb_max=dict(
            type='int', required=False, default=4,
            aliases=['maximum_object_size', 'max_size'],
            description='The maximum object size'
        ),
        memory_kb_max=dict(
            type='int', required=False, default=512,
            aliases=['maximum_object_size_in_memory', 'max_memory', 'max_mem'],
            description='The maximum object size'
        ),
        memory_cache_mode=dict(
            type='str', required=False, default='default',
            aliases=['cache_mode', 'mode'],
            choices=['always', 'disk', 'network', 'default'],
            description='Controls which objects to keep in the memory cache (cache_mem) always: '
                        'Keep most recently fetched objects in memory (default) disk: Only disk '
                        'cache hits are kept in memory, which means an object must first be '
                        'cached on disk and then hit a second time before cached in memory. '
                        'network: Only objects fetched from network is kept in memory'
        ),
        cache_linux_packages=dict(
            type='bool', required=False, default=False,
            description='Enable or disable the caching of packages for linux distributions. '
                        'This makes sense if you have multiple servers in your network and do '
                        'not host your own package mirror. This will reduce internet traffic '
                        'usage but increase disk access'
        ),
        cache_windows_updates=dict(
            type='bool', required=False, default=False,
            description='Enable or disable the caching of Windows updates. This makes sense '
                        "if you don't have a WSUS server. If you can setup a WSUS server, "
                        'this solution should be preferred'
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

    for field, value in BLANK_VALUES.items():
        if module.params[field] == value:
            module.params[field] = ''  # BlankDesc

    module_wrapper(Cache(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
