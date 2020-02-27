from base_app import BaseApp

from local_config import occupancy as config


class Occupancy(BaseApp):
    def initialize(self):
        for sensor, data in config['sensors'].items():
            self.listen_state(self.motion, sensor)

    def motion(self, entity, attribute, old, new, kwargs):
        if new == 'off':
            return

        sensor = config['sensors'][entity]
        # Check that this timer is not disabled by its enabling_boolean
        if self.get_state(sensor['enabling_boolean']) == 'off':
            return

        self.log(config['log_msg'].format(**sensor))
        for light in sensor['lights']:
            light = self.get_app('lights').get_light(light)
            light.occ_turn_on()
