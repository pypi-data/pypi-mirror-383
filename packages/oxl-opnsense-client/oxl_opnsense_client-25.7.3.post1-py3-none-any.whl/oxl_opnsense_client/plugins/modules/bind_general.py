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
    from plugins.module_utils.main.bind_general import General

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/bind.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/bind.html'


def run_module(module_input):
    module_args = dict(
        ipv6=dict(
            type='bool', required=False, default=True, aliases=['v6'],
            description='If IPv6 should be enabled'
        ),
        response_policy_zones=dict(
            type='bool', required=False, default=True,
            aliases=['rpz'],
            description='If response-policy-zones should be enabled'
        ),
        port=dict(
            type='int', required=False, aliases=['p'], default=53530,
            description='Port the service should listen on'
        ),
        listen_ipv4=dict(
            type='list', elements='str', required=False, default=['127.0.0.1'],
            aliases=['listen_v4', 'listen'],
            description='IPv4 addresses the service should listen on'
        ),
        listen_ipv6=dict(
            type='list', elements='str', required=False, default=['::1'],
            aliases=['listen_v6'],
            description='IPv6 addresses the service should listen on'
        ),
        query_source_ipv4=dict(
            type='str', required=False,
            aliases=['query_ipv4', 'query_v4'],
            description='Specify the IPv4 address used as a source for outbound queries'
        ),
        query_source_ipv6=dict(
            type='str', required=False,
            aliases=['query_ipv6', 'query_v6'],
            description='Specify the IPv6 address used as a source for outbound queries'
        ),
        transfer_source_ipv4=dict(
            type='str', required=False,
            aliases=['transfer_ipv4', 'transfer_v4'],
            description='Specify the IPv4 address used as a source for zone transfers'
        ),
        transfer_source_ipv6=dict(
            type='str', required=False,
            aliases=['transfer_ipv6', 'transfer_v6'],
            description='Specify the IPv6 address used as a source for zone transfers'
        ),
        forwarders=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['fwd'],
            description='Set one or more hosts to send your DNS queries if the request is unknown'
        ),
        filter_aaaa_v4=dict(
            type='bool', required=False, default=False,
            description='This will filter AAAA records on IPv4 Clients'
        ),
        filter_aaaa_v6=dict(
            type='bool', required=False, default=False,
            description='This will filter AAAA records on IPv6 Clients'
        ),
        filter_aaaa_acl=dict(
            type='list', elements='str', required=False, default=[],
            description='Specifies a list of client addresses for which AAAA filtering is to be applied'
        ),
        log_size=dict(
            type='int', required=False, default=5, aliases=['max_log_size'],
            description='Maximum log file size in MB'
        ),
        cache_size=dict(
            type='int', required=False, default=50,
            aliases=['max_cache_size', 'cache_percentage', 'max_cache_percentage'],
            description='How much memory in percent the cache can use from the system'
        ),
        recursion_acl=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['recursion'],
            description='Define an ACL where you allow which clients can resolve via '
                        'this service. Usually use your local LAN'
        ),
        transfer_acl=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['allow_transfer', 'transfer'],
            description='Define the ACLs where you allow which server can retrieve zones'
        ),
        query_acl=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['allow_query', 'query'],
            description='Define the ACLs where you allow which client are allowed to query this server'
        ),
        dnssec_validation=dict(
            type='str', required=False, default='no',
            aliases=['dnssec'], choices=['no', 'auto'],
            description='Set to "Auto" to use the static trust anchor configuration by the system'
        ),
        hide_hostname=dict(
            type='bool', required=False, default=False,
            description='This will hide the system hostname for DNS queries'
        ),
        hide_version=dict(
            type='bool', required=False, default=True,
            description='This will hide the local BIND version in DNS queries'
        ),
        prefetch=dict(
            type='bool', required=False, default=True,
            description='If prefetching of domains should be enabled'
        ),
        ratelimit=dict(
            type='bool', required=False, default=False,
            description='This will enable rate-limiting for DNS replies'
        ),
        ratelimit_count=dict(
            type='str', required=False,
            description='Set how many replies per second are allowed'
        ),
        ratelimit_except=dict(
            type='list', elements='str', required=False,
            default=['127.0.0.1', '::1'],
            description='Except a list of IPs from rate-limiting'
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

    module_wrapper(General(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
