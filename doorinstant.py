from base_app import BaseApp
from local_config import door_instant as config


class DoorInstant(BaseApp):
    """
    Use this for covers/doors when you want inmediate notification
    of openings and closings (for example, the entrance door).
    """
    def initialize(self):
        for entity in config.keys():
            self.listen_state(self.check_door, entity)

    def check_door(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        data = config[entity]
        if new == data['open_state']:
            self.smart_notify(data['notifiers'], data['open_msg'])
        elif new == data['closed_state']:
            self.smart_notify(data['notifiers'], data['closed_msg'])
