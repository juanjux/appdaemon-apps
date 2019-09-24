import threading

from has_logging_app import HASLoggingApp

from occupancy_sensors import sensors


class Occupancy(HASLoggingApp):
    def initialize(self):
        for sensor, data in sensors.items():
            self.listen_state(self.motion, sensor)

    def motion(self, entity, attribute, old, new, kwargs):
        if new == 'off':
            return

        sensor = sensors[entity]
        # Check that this timer is not disabled by its enabling_boolean
        if self.get_state(sensor['enabling_boolean']) == 'off':
            return

        self.log('Motion detected on {}'.format(sensor['zone']))
        light = self.global_vars['lights'][sensor['light']]
        light.occ_turn_on()
