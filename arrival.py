from base_app import BaseApp
from local_config import arrival as config


class Arrival(BaseApp):
    """
    Notify when somebody arrives
    """
    def initialize(self):
        self.listen_state(self.arrived, 'device_tracker')

    def arrived(self, entity, attribute, old, new, kwargs):
        if old != 'not_home' or new != 'home' or entity not in config:
            return

        notify_data = config[entity]
        self.smart_notify(notify_data['notifiers'], notify_data['msg'])
