from has_logging_app import HASLoggingApp

from occupancy_sensors import sensors


class OccupancyAlarm(HASLoggingApp):
    """
    Produce an alarm using pushover if the external occupancy
    sensors detect movement
    """
    def initialize(self):
        self.timer_handle = None

        for sensor, data in sensors.items():
            if data['is_outside']:
                self.listen_state(self.motion, sensor, data=data)

    def motion(self, entity, attribute, old, new, kwargs):
        if new == 'off' or new == old:
            return

        msg = 'Movement detected in {zone}'.format(**kwargs['data'])
        self.call_service('notify/pushover',
                title='MOVEMENT ALARM',
                message = msg,
                data={
                    'sound': 'persistent',
                    'priority': 1,
                    'url': ''
                    })
