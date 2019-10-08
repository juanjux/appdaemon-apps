from base_app import BaseApp
from local_config import leak_notify as config


class LeakNotify(BaseApp):
    def initialize(self):
        for s in config['leak_sensors']:
            self.listen_state(self.leak, s)

    def leak(self, entity, attribute, old, new, kwargs):
        if new == 'off' or old == 'on':
            return

        # The sensors sometimes do quick false positives, put small timeout
        # to check it again and only then turn off the switches
        self.run_in(self.recheck_cb, config['recheck_timeout'])

    def recheck_cb(self, kwargs):
        for s in config['leak_sensors']:
            state = self.get_state(s)

            if state != 'on':
                continue

            self.log('Water leak detected on {}'.format(s))
            self.smart_notify(config['notifiers'], config['msg'].format(sensor=s))
