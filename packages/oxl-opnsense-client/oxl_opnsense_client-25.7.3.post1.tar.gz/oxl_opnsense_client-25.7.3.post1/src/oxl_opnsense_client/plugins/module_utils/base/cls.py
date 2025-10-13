from basic.ansible import AnsibleModule

from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.base.base import Base
from plugins.module_utils.helper.validate import \
    validate_int_fields, validate_str_fields


class BaseShared:
    def __init__(self, m: AnsibleModule, r: dict, s: Session):
        if hasattr(self, 'TIMEOUT'):
            self.s = Session(
                module=m,
                timeout=self.TIMEOUT,
            ) if s is None else s

        else:
            self.s = Session(module=m) if s is None else s

        self.m = m
        self.p = m.params
        self.r = r
        self.b = Base(instance=self)
        self.exists = False
        self.existing_entries = None
        self.call_cnf = {
            'module': self.b.i.API_MOD,
            'controller': self.b.i.API_CONT,
        }

    def _check_validators(self):
        if 'state' in self.p and self.p['state'] != 'present':
            return

        if hasattr(self.b.i, 'STR_VALIDATIONS'):
            if hasattr(self.b.i, 'STR_LEN_VALIDATIONS'):
                validate_str_fields(
                    module=self.m,
                    data=self.p,
                    field_regex=self.b.i.STR_VALIDATIONS,
                    field_minmax_length=self.b.i.STR_LEN_VALIDATIONS
                )

            else:
                validate_str_fields(module=self.m, data=self.p, field_regex=self.b.i.STR_VALIDATIONS)

        elif hasattr(self.b.i, 'STR_LEN_VALIDATIONS'):
            validate_str_fields(module=self.m, data=self.p, field_minmax_length=self.b.i.STR_LEN_VALIDATIONS)

        if hasattr(self.b.i, 'INT_VALIDATIONS'):
            validate_int_fields(module=self.m, data=self.p, field_minmax=self.b.i.INT_VALIDATIONS)


class BaseModule(BaseShared):
    def __init__(self, m: AnsibleModule, r: dict, s: Session = None, f: dict = None, multi: dict = None):
        super().__init__(m, r, s)
        if f is None:
            f = {}

        if multi is not None and len(multi) > 0:
            # override params by MultiModule
            self.p = multi

        self.fail_verify = f.get('verify', False)
        self.fail_process = f.get('process', False)

    def _base_check(self, match_fields: list = None):
        self._check_validators()

        if match_fields is None:
            if 'match_fields' in self.p:
                match_fields = self.p['match_fields']

            elif hasattr(self, 'FIELD_ID'):
                match_fields = [self.FIELD_ID]

        if match_fields is not None:
            self.b.find(match_fields=match_fields)
            if self.exists:
                self.call_cnf['params'] = [getattr(self, self.EXIST_ATTR)[self.b.field_pk]]

        if 'state' not in self.p or self.p['state'] == 'present':
            self.r['diff']['after'] = self.b.build_diff(data=self.p)

    def check(self) -> None:
        self._base_check()

    def get_existing(self) -> list:
        return self.b.get_existing()

    def process(self) -> None:
        self.b.process()

    def create(self) -> None:
        self.b.create()

    def update(self) -> None:
        self.b.update()

    def delete(self) -> None:
        self.b.delete()

    def reload(self) -> None:
        self.b.reload()


class GeneralModule(BaseShared):
    # has only a single entry; cannot be deleted or created
    EXIST_ATTR = 'settings'

    def __init__(self, m: AnsibleModule, r: dict, s: Session = None):
        super().__init__(m, r, s)
        self.settings = {}

    def _base_check(self):
        self._check_validators()
        self.settings = self._search_call()
        self._build_diff()

    def check(self) -> None:
        self._base_check()

    def _search_call(self) -> dict:
        return self.b.simplify_existing(self.b.search())

    def get_existing(self) -> dict:
        return self._search_call()

    def process(self) -> None:
        self.update()

    def update(self) -> None:
        self.b.update(enable_switch=False)

    def reload(self) -> None:
        self.b.reload()

    def _build_diff(self) -> None:
        self.r['diff']['before'] = self.b.build_diff(self.settings)
        self.r['diff']['after'] = self.b.build_diff({
            k: v for k, v in self.p.items() if k in self.settings
        })
