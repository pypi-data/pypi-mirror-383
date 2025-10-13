from ..module_input import validate_input, ModuleInput, valid_results
from ..module_utils.helper.wrapper import module_wrapper
from ..module_utils.defaults.main import STATE_MOD_ARG, RELOAD_MOD_ARG
from ..module_utils.main.frr_bgp_neighbor import Neighbor


def run_module(module_input: ModuleInput, result: dict = None) -> dict:
    result = valid_results(result)

    module_args = dict(
        ip=dict(
            type='str', required=False,
            aliases=['neighbor', 'peer', 'peer_ip', 'address'],
        ),
        as_number=dict(
            type='int', required=False, aliases=['as', 'as_nr', 'remote_as']
        ),
        password=dict(
            type='str', required=False, aliases=['pwd'], no_log=True,
            description='Set a (MD5-hashed) password for BGP authentication.'
        ),
        weight=dict(type='int', required=False),
        local_ip=dict(
            type='str', required=False, aliases=['local'],
            description='Set the local IP connecting to the neighbor. '
                        'This is only required for BGP authentication.'
        ),
        source_int=dict(
            type='str', required=False,
            aliases=['update_source', 'update_src', 'src_int'],
            description='Physical name of the IPv4 interface facing the peer'
        ),
        ipv6_link_local_int=dict(
            type='str', required=False,
            aliases=['link_local_int', 'ipv6_ll_int', 'v6_ll_int'],
            description='Interface to use for IPv6 link-local neighbours'
        ),
        next_hop_self=dict(
            type='bool', required=False, default=False, aliases=['nhs']
        ),
        next_hop_self_all=dict(
            type='bool', required=False, default=False, aliases=['nhsa'],
            description='Add the parameter "all" after next-hop-self command'
        ),
        multi_hop=dict(
            type='bool', required=False, default=False,
            description='Specifying ebgp-multihop allows sessions with '
                        'eBGP neighbors to establish when they are multiple '
                        'hops away. When the neighbor is not directly connected '
                        'and this knob is not enabled, the session will not establish.'
        ),
        multi_protocol=dict(
            type='bool', required=False, default=False,
            description='Is this neighbour multiprotocol capable per RFC 2283'
        ),
        rrclient=dict(
            type='bool', required=False, default=False,
            aliases=['route_reflector_client']
        ),
        bfd=dict(
            type='bool', required=False, default=False,
            description='Enable BFD support for this neighbor.'
        ),
        send_default_route=dict(
            type='bool', required=False, default=False, aliases=['default_originate'],
        ),
        as_override=dict(
            type='bool', required=False, default=False, aliases=['asoverride'],
            description='Override AS number of the originating router with the local '
                        'AS number. This command is only allowed for eBGP peers.'
        ),
        disable_connected_check=dict(
            type='bool', required=False, default=False,
            description='Allow peerings between directly connected eBGP peers using '
                        'loopback addresses.'
        ),
        keepalive=dict(
            type='int', required=False, default=60, aliases=['keep_alive'],
            description='Keepalive timer to check if the neighbor is still up.'
        ),
        hold_down=dict(
            type='int', required=False, default=180, aliases=['holddown'],
            description='The time in seconds when a neighbor is considered dead. '
                        'This is usually 3 times the keepalive timer'
        ),
        connect_timer=dict(
            type='int', required=False, aliases=['connecttimer'],
            description='The time in seconds how fast a neighbor tries to reconnect.'
        ),
        description=dict(type='str', required=False, aliases=['desc']),
        prefix_list_in=dict(
            type='str', required=False, aliases=['prefix_in', 'pre_in']
        ),
        prefix_list_out=dict(
            type='str', required=False, aliases=['prefix_out', 'pre_out']
        ),
        route_map_in=dict(
            type='str', required=False, aliases=['map_in', 'rm_in']
        ),
        route_map_out=dict(
            type='str', required=False, aliases=['map_out', 'rm_out']
        ),
        match_fields=dict(
            type='list', required=False, elements='str',
            description='Fields that are used to match configured neighbors with the running config - '
                        "if any of those fields are changed, the module will think it's a new entry",
            choices=[
                'ip', 'as_number', 'weight', 'local_ip', 'source_int',
                'ipv6_link_local_int', 'disable_connected_check', 'description',
                'prefix_list_in', 'prefix_list_out', 'route_map_in', 'route_map_out',
            ],
            default=['ip', 'description'],
        ),
        **STATE_MOD_ARG,
        **RELOAD_MOD_ARG,
    )

    validate_input(i=module_input, definition=module_args)
    module_wrapper(Neighbor(m=module_input, result=result))
    return result
