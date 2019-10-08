from datetime import datetime, timedelta
from base_app import BaseApp
from local_config import dooropen_warning as config


class DoorOpenWarning(BaseApp):
    """
    Warn if a door/doors is/are opened after some time configured in apps.yaml
    """

    def initialize(self):
        now = datetime.now() + timedelta(seconds=5)
        self.run_every(self.door_open_cb, now, config['interval'])

    def door_open_cb(self, kwargs):
        for entity, data in config['entities'].items():
            if self.get_state(entity) == data['open_state']:
                self.smart_notify(config['notifiers'], data['msg'])
