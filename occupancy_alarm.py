from base_app import BaseApp

from local_config import occupancy_alarm as config
from local_config import occupancy


class OccupancyAlarm(BaseApp):
    """
    Send a notification if movement is detected on any of the outside
    motion detectors. Use a constraint_input_boolean to enable or disable
    it at will (e.g. when outside the house or in holidays mode).
    """
    def initialize(self):
        self.timer_handle = None

        for sensor, data in occupancy['sensors'].items():
            if data['is_outside']:
                self.listen_state(self.motion, sensor, data=data)

    def motion(self, entity, attribute, old, new, kwargs):
        if new == 'off' or new == old:
            return

        msg = config['msg'].format(**kwargs['data'])
        self.smart_notify(config['notifiers'], msg)
