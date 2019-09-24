from has_logging_app import HASLoggingApp

from door_sensors import sensors


class DoorAlarm(HASLoggingApp):
    """
    Produce an alarm using pushover if a door is opened
    """
    def initialize(self):
        for name, data in sensors.items():
            self.listen_state(self.check_door, name, data=data)

    def check_door(self, entity, attribute, old, new, kwargs):
        if new == 'off' or new == old:
            return

        msg = '{type} {name} opened!'.format(**kwargs['data'])

        self.call_service('notify/pushover',
                title='OPEN DOOR ALERT!',
                message = msg,
                data={
                    'sound': 'persistent',
                    'priority': 2,
                    'retry': 30,
                    'expire': 10800,
                    'url': ''
                    })
