from base_app import BaseApp
from local_config import rain_switcher as config


class RainSwitcher(BaseApp):
    """
    Turn off power to external lights (either using Sonoff Basic/Shelly
    modules or neutral-powered smart wall switches) when in rain to avoid
    short circuits on not-so-well isolated circuits.
    """
    def initialize(self):
        self.listen_state(self.raining, config['rain_sensor'])

    def raining(self, entity, attribute, old, new, kwargs):
        if new == 'off' or old == 'on':
            return

        # The sensor sometimes do quick false positives, put a 10 seconds timeout
        # to check it again and only then turn off the switches
        self.run_in(self.recheck_cb, 10)

    def recheck_cb(self, kwargs):
        state = self.get_state(config['rain_sensor'])
        if state != 'on':
            return

        some_turned_off = False
        for i in config['to_turnoff']:
            s = self.get_state(i)
            if s == 'on':
                self.turn_off(i)
                some_turned_off = True

        if some_turned_off:
            self.log('Rain detected, some switches turned off')
            self.smart_notify(config['notifiers'], config['msg'])
