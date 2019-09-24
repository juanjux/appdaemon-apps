from has_logging_app import HASLoggingApp


class NotificationWaterLeak(HASLoggingApp):
    def initialize(self):
        # Add all water leak sensors here
        self.listen_state(self.raining, 'binary_sensor.water_leak')

    def raining(self, entity, attribute, old, new, kwargs):
        if new == 'off' or old == 'on':
            return

        # to avoid quick false positives, put a 10 seconds timeout
        # to check it again and only then turn off the switches
        self.run_in(self.recheck_cb, 10)

    def recheck_cb(self, kwargs):
        state = self.get_state('binary_sensor.water_leak')
        if state != 'on':
            return

        for i in ['somenotification_service']:
            self.call_service('notify/%s' % i,
                    message='Water leak detected!')
