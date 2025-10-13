from ..module_input import validate_input, ModuleInput, valid_results
from ..module_utils.helper.wrapper import module_wrapper
from ..module_utils.defaults.main import STATE_MOD_ARG, RELOAD_MOD_ARG
from ..module_utils.defaults.openvpn import OPENVPN_INSTANCE_MOD_ARGS
from ..module_utils.main.openvpn_server import Server


def run_module(module_input: ModuleInput, result: dict = None) -> dict:
    result = valid_results(result)

    module_args = dict(
        # general
        port=dict(
            type='int', required=False, default=1194, aliases=['local_port', 'bind_port'],
            description='Port number to use'
        ),
        server_ip4=dict(
            type='str', required=False, aliases=['server', 'client_net_ip4', 'net_ip4'],
            description='This directive will set up an OpenVPN server which will allocate addresses to clients '
                        'out of the given network/netmask. The server itself will take the .1 address of the given '
                        'network for use as the server-side endpoint of the local TUN/TAP interface'
        ),
        server_ip6=dict(
            type='str', required=False, aliases=['server6', 'client_net_ip6', 'net_ip6'],
            description='This directive will set up an OpenVPN server which will allocate addresses to clients '
                        'out of the given network/netmask. The server itself will take the next base address (+1) '
                        'of the given network for use as the server-side endpoint of the local TUN/TAP interface'
        ),
        max_connections=dict(
            type='int', required=False, aliases=['max_conn', 'max_clients'],
            description='Specify the maximum number of clients allowed to concurrently connect to this server.'
        ),
        topology=dict(
            type='str', required=False, default='subnet', aliases=['topo'],
            choices=['net30', 'p2p', 'subnet'],
            description='Configure virtual addressing topology when running in --dev tun mode. This directive '
                        'has no meaning in --dev tap mode, which always uses a subnet topology.'
        ),
        # trust
        crl=dict(
            type='str', required=False, aliases=['certificate_revocation_list', 'revocation_list'],
            description='Select a certificate revocation list to use for this service.'
        ),
        verify_client_cert=dict(
            type='str', required=False, default='require', aliases=['verify_client', 'verify_cert'],
            choices=['require', 'none'],
            description='Specify if the client is required to offer a certificate.'
        ),
        cert_depth=dict(
            type='int', required=False, aliases=['certificate_depth'],
            choices=[1, 2, 3, 4, 5],
            description='When a certificate-based client logs in, do not accept certificates below this depth. '
                        'Useful for denying certificates made with intermediate CAs generated from the same CA as '
                        'the server. '
                        '0 = Do not check, 1 = Client+Server, 2 = Client+Intermediate+Server, '
                        '3 = Client+2xInter+Server, 4 = Client+3xInter+Server, '
                        '5 = Client+4xInter+Server'
        ),
        data_ciphers=dict(
            type='list', elements='str', required=False, default=[], aliases=['ciphers'],
            choices=['AES-256-GCM', 'AES-128-GCM', 'CHACHA20-POLY1305'],
            description='Restrict the allowed ciphers to be negotiated to the ciphers in this list.'
        ),
        data_cipher_fallback=dict(
            type='str', required=False, aliases=['cipher_fallback'],
            choices=['AES-256-GCM', 'AES-128-GCM', 'CHACHA20-POLY1305'],
            description='Configure a cipher that is used to fall back to if we could not determine which cipher the '
                        'peer is willing to use. This option should only be needed to connect to peers that are '
                        'running OpenVPN 2.3 or older versions, and have been configured with --enable-small '
                        '(typically used on routers or other embedded devices).'
        ),
        ocsp=dict(
            type='bool', required=False, default=False, aliases=['use_ocsp', 'verify_ocsp'],
            description='When the CA used supplies an authorityInfoAccess OCSP URI extension, '
                        'it will be used to validate the client certificate.'
        ),
        # authentication
        auth_mode=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['authentication_mode', 'auth_source'],
            description='Select authentication methods to use, leave empty if no challenge response '
                        'authentication is needed.'
        ),
        auth_group=dict(
            type='str', required=False, aliases=['group'],
            description='Restrict access to users in the selected local group. Please be aware that other '
                        'authentication backends will refuse to authenticate when using this option.'
        ),
        user_as_cn=dict(
            type='bool', required=False, default=False, aliases=['username_as_cn'],
            description='Use the authenticated username as the common-name, rather than the common-name '
                        'from the client certificate.'
        ),
        user_cn_strict=dict(
            type='bool', required=False, default=False, aliases=['username_cn_strict'],
            description='When authenticating users, enforce a match between the Common Name of the client '
                        'certificate and the username given at login.'
        ),
        auth_token_time=dict(
            type='int', required=False, aliases=['auth_time', 'token_time'],
            description='After successful user/password authentication, the OpenVPN server will with this option '
                        'generate a temporary authentication token and push that to the client. On the following '
                        'renegotiations, the OpenVPN client will pass this token instead of the users password. '
                        'On the server side the server will do the token authentication internally and it will NOT '
                        'do any additional authentications against configured external user/password authentication '
                        'mechanisms. When set to 0, the token will never expire, any other value specifies the '
                        'lifetime in seconds.'
        ),
        # misc
        push_options=dict(
            type='list', elements='str', required=False, default=[], aliases=['push_opts'],
            choices=['block-outside-dns', 'register-dns'],
            description='Various less frequently used yes/no options which can be pushed to the client '
                        'for this instance.',
        ),
        redirect_gateway=dict(
            type='list', elements='str', required=False, default=[], aliases=['redirect_gw', 'redir_gw'],
            choices=['local', 'autolocal', 'def1', 'bypass_dhcp', 'bypass_dns', 'block_local', 'ipv6', 'notipv4'],
            description='Automatically execute routing commands to cause all outgoing IP traffic to be '
                        'redirected over the VPN.',
        ),
        route_metric=dict(
            type='int', required=False, aliases=['metric', 'push_metric'],
            description='Specify a default metric m for use with --route on the connecting client (push option).'
        ),
        register_dns=dict(
            type='bool', required=False, default=False,
            description='Run ipconfig /flushdns and ipconfig /registerdns on connection initiation. '
                        'This is known to kick Windows into recognizing pushed DNS servers.'
        ),
        domain=dict(
            type='str', required=False, aliases=['dns_domain'],
            description='Set Connection-specific DNS Suffix.'
        ),
        domain_list=dict(
            type='list', elements='str', required=False, default=[], aliases=['dns_domain_search'],
            description='Add name to the domain search list. Repeat this option to add more entries. '
                        'Up to 10 domains are supported'
        ),
        dns_servers=dict(
            type='list', elements='str', required=False, default=[], aliases=['dns'],
            description='Set primary domain name server IPv4 or IPv6 address. '
                        'Repeat this option to set secondary DNS server addresses.'
        ),
        ntp_servers=dict(
            type='list', elements='str', required=False, default=[], aliases=['ntp'],
            description='Set primary NTP server address (Network Time Protocol). '
                        'Repeat this option to set secondary NTP server addresses.'
        ),
        **OPENVPN_INSTANCE_MOD_ARGS,
        **RELOAD_MOD_ARG,
        **STATE_MOD_ARG,
    )


    validate_input(i=module_input, definition=module_args)
    module_wrapper(Server(m=module_input, result=result))
    return result
