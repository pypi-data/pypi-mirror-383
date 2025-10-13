from ..helper.main import  validate_int_fields, is_unset
from ..base.cls import BaseModule


class Pipe(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'addPipe',
        'del': 'delPipe',
        'set': 'setPipe',
        'search': 'get',
        'toggle': 'togglePipe',
    }
    API_KEY_PATH = 'ts.pipes.pipe'
    API_MOD = 'trafficshaper'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'bandwidth', 'bandwidth_metric', 'queue', 'mask', 'buckets', 'scheduler',
        'codel_enable', 'codel_target', 'codel_interval', 'codel_ecn_enable',
        'pie_enable', 'fqcodel_quantum', 'fqcodel_limit', 'fqcodel_flows',
        'delay',
    ]
    FIELDS_ALL = ['enabled', FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'bandwidth_metric': 'bandwidthMetric',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'pie_enable', 'codel_enable', 'codel_ecn_enable'],
        'select': ['bandwidth_metric', 'mask', 'scheduler'],
    }
    INT_VALIDATIONS = {
        # 'id': {'min': 1, 'max': 65535},
        'queue': {'min': 2, 'max': 100},
        'buckets': {'min': 1, 'max': 65535},
        'codel_target': {'min': 1, 'max': 10000},
        'codel_interval': {'min': 1, 'max': 10000},
        'fqcodel_quantum': {'min': 1, 'max': 65535},
        'fqcodel_limit': {'min': 1, 'max': 65535},
        'fqcodel_flows': {'min': 1, 'max': 65535},
        'delay': {'min': 1, 'max': 3000},
    }
    EXIST_ATTR = 'pipe'
    TIMEOUT = 20.0  # 'get' timeout

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.pipe = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

            if is_unset(self.p['bandwidth']):
                self.m.fail('You need to provide bandwidth to create a shaper pipe!')

        self._base_check()

    def reload(self) -> None:
        if self.p['reset']:
            self.API_CMD_REL = 'flushreload'

        self.b.reload()
