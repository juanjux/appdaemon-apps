from has_logging_app import HASLoggingApp

danger_switches = [
        'switch.some_light_that_can_get_wet_on_rain',
]


class NotificationRain(HASLoggingApp):
    def initialize(self):
        self.listen_state(self.raining, 'binary_sensor.rain_leak')

    def raining(self, entity, attribute, old, new, kwargs):
        if new == 'off' or old == 'on':
            return

        # The sensor sometimes do quick false positives, put a 10 seconds timeout
        # to check it again and only then turn off the switches
        self.run_in(self.recheck_cb, 10)

    def recheck_cb(self, kwargs):
        state = self.get_state('binary_sensor.rain_leak')
        if state != 'on':
            return

        some_turned_off = False
        for i in danger_switches:
            s = self.get_state(i)
            if s == 'on':
                self.turn_off(i)
                some_turned_off = True

        if some_turned_off:
            for i in ['some_notification_service']:
                self.call_service('notify/%s' % i,
                        message='Rain detected, cutting power to outside lights')
