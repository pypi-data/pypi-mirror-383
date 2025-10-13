from ..helper.main import is_unset
from ..helper.purge import purge, check_purge_filter
from ..helper.rule import check_purge_configured
from ..main.rule import Rule


def process(m, p: dict, r: dict) -> None:
    existing_rules = Rule(m=m, result={}).get_existing()
    rules_to_purge = []

    def obj_func(rule_to_purge: dict) -> Rule:
        if 'debug' not in rule_to_purge:
            rule_to_purge['debug'] = p['debug']

        if rule_to_purge['debug'] or p['output_info']:
            m.warn(f"Purging rule '{rule_to_purge[p['key_field']]}'!")

        _rule = Rule(
            m=m,
            result={'changed': False, 'diff': {'before': {}, 'after': {}}},
            cnf=rule_to_purge,
            fail_verify=p['fail_all'],
            fail_proc=p['fail_all'],
        )
        _rule.rule = rule_to_purge
        _rule.call_cnf['params'] = [rule_to_purge['uuid']]
        return _rule

    # checking if all rules should be purged
    if not p['force_all'] and is_unset(p['rules']) and \
            is_unset(p['filters']):
        m.fail("You need to either provide 'rules' or 'filters'!")

    if len(existing_rules) > 0:
        if p['force_all'] and is_unset(p['rules']) and \
                is_unset(p['filters']):
            m.warn('Forced to purge ALL RULES!')

            for existing_rule in existing_rules:
                purge(
                    m=m, result=r, obj_func=obj_func,
                    diff_param=p['key_field'],
                    item_to_purge=existing_rule,
                )

        else:
            # checking if existing rule should be purged
            for existing_rule in existing_rules:
                to_purge = check_purge_configured(m=m, existing_rule=existing_rule)

                if to_purge:
                    to_purge = check_purge_filter(m=m, item=existing_rule)

                if to_purge:
                    if p['debug']:
                        m.warn(
                            f"Existing rule '{existing_rule[p['key_field']]}' "
                            f"will be purged!"
                        )

                    rules_to_purge.append(existing_rule)

            for rule in rules_to_purge:
                r['changed'] = True
                purge(
                    m=m, result=r, diff_param=p['key_field'],
                    obj_func=obj_func, item_to_purge=rule
                )
