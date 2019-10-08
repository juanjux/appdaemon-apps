from base_app import BaseApp

from local_config import door_alarm as config
from local_config import HOLIDAYS_MODE_BOOLEAN


class DoorAlarm(BaseApp):
    def initialize(self):
        for name, data in config['sensors'].items():
            self.listen_state(self.check_door, name, data=data)

    def check_door(self, entity, attribute, old, new, kwargs):
        d = kwargs['data']
        if new == old or new != d['open_status']:
            return

        if self.get_state(HOLIDAYS_MODE_BOOLEAN) == 'off' and\
                not d['warn_nonholidays']:
                    return

        msg = config['msg'].format(**d)
        self.smart_notify(config['notifiers'], msg)
