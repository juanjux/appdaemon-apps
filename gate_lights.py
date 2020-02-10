from base_app import BaseApp

from local_config import gate_lights as config


class GateLights(BaseApp):
    def initialize(self):
        for name, data in config['gates'].items():
            self.listen_state(self.check_door, name, data=data)

    def check_door(self, entity, attribute, old, new, kwargs):
        d = kwargs['data']
        if new == old or new != d['open_status']:
            return

        for l in config['gates'][entity]['lights']:
            self.turn_on(l)

        self.run_in(self.lights_off_cb, config['lights_timeout'], entity=entity)

    def lights_off_cb(self, kwargs):
        for l in config['gates'][kwargs['entity']]['lights']:
            self.turn_off(l)
