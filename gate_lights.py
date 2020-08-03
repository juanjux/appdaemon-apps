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
            st = self.get_state(l)
            if st != 'on':
                self.turn_on(l)
                self.run_in(self.light_off_cb, config['gates'][entity]['lights_timeout'],
                            light=l)

    def light_off_cb(self, kwargs):
        self.turn_off(kwargs['light'])
