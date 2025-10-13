from ..module_input import validate_input, ModuleInput, valid_results
from ..module_utils.helper.wrapper import module_wrapper
from ..module_utils.defaults.main import RELOAD_MOD_ARG
from ..module_utils.main.webproxy_forward import General


def run_module(module_input: ModuleInput, result: dict = None) -> dict:
    result = valid_results(result)

    module_args = dict(
        interfaces=dict(
            type='list', elements='str', required=False, default=['lan'], aliases=['ints'],
            description='Interface(s) the proxy will bind to'
        ),
        port=dict(type='int', required=False, default=3128, aliases=['p']),
        port_ssl=dict(type='int', required=False, default=3129, aliases=['p_ssl']),
        transparent=dict(
            type='bool', required=False, default=False, aliases=['transparent_mode'],
            description='Enable transparent proxy mode. You will need a firewall rule to '
                        'forward traffic from the firewall to the proxy server. You may '
                        'leave the proxy interfaces empty, but remember to set a valid ACL '
                        'in that case'
        ),
        ssl_inspection=dict(
            type='bool', required=False, default=False, aliases=['ssl_inspect', 'ssl'],
            description='Enable SSL inspection mode, which allows to log HTTPS connections '
                        'information, such as requested URL and/or make the proxy act as a '
                        'man in the middle between the internet and your clients. Be aware '
                        'of the security implications before enabling this option. If you '
                        'plan to use transparent HTTPS mode, you need nat rules to reflect '
                        'your traffic'
        ),
        ssl_inspection_sni_only=dict(
            type='bool', required=False, default=False, aliases=['ssl_sni_only'],
            description='Do not decode and/or filter SSL content, only log requested domains '
                        'and IP addresses. Some old servers may not provide SNI, so their '
                        'addresses will not be indicated'
        ),
        ssl_ca=dict(
            type='str', required=False, aliases=['ca'],
            description='Select a Certificate Authority to use'
        ),
        ssl_exclude=dict(
            type='list', elements='str', required=False, default=[],
            description='A list of sites which may not be inspected, for example bank sites. '
                        'Prefix the domain with a . to accept all subdomains (e.g. .google.com)'
        ),
        ssl_cache_mb=dict(
            type='int', required=False, default=4, aliases=['ssl_cache', 'cache'],
            description='The maximum size (in MB) to use for SSL certificates'
        ),
        ssl_workers=dict(
            type='int', required=False, default=5, aliases=['workers'],
            description='The number of ssl certificate workers to use (sslcrtd_children)'
        ),
        allow_interface_subnets=dict(
            type='bool', required=False, default=True, aliases=['allow_subnets'],
            description='When enabled the subnets of the selected interfaces will be '
                        'added to the allow access list'
        ),
        # snmp tab
        snmp=dict(
            type='bool', required=False, default=False,
            description='Enable or disable the squid SNMP Agent'
        ),
        port_snmp=dict(type='int', required=False, default=3401, aliases=['p_snmp']),
        snmp_password=dict(
            type='str', required=False, default='public', no_log=True,
            aliases=['snmp_community', 'snmp_pwd'],
            description='The password for access to SNMP agent'
        ),
        # ftp tab
        interfaces_ftp=dict(
            type='list', elements='str', required=False, default=[], aliases=['ints_ftp'],
            description='Interface(s) the ftp proxy will bind to'
        ),
        port_ftp=dict(type='int', required=False, default=2121, aliases=['p_ftp']),
        transparent_ftp=dict(
            type='bool', required=False, default=False,
            description='Enable transparent ftp proxy mode to forward all requests '
                        'for destination port 21 to the proxy server without any '
                        'additional configuration'
        ),
        **RELOAD_MOD_ARG,
    )

    validate_input(i=module_input, definition=module_args)
    module_wrapper(General(m=module_input, result=result))
    return result
