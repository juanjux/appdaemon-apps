import datetime

from base_app import BaseApp
from local_config import yeelight_nightmode as config


class YeelightNightMode(BaseApp):
    def initialize(self):
        self.start_timers()

    def clicked(self, entity, attribute, old, new, kwargs):
        self.cancel_timers()

        if new == 'on':
            # Ensure the timer is updated in case we changed the dates
            self.start_timers()

    def start_timers(self):
        self.timer_start = self.run_daily(self.timer_start_cb, config['start_time'])
        self.timer_stop = self.run_daily(self.timer_stop_cb, config['end_time'])

    def cancel_timers(self):
        self.cancel_timer(self.timer_start)
        self.timer_start = None

        self.cancel_timer(self.timer_stop)
        self.timer_stop = None

    def timer_start_cb(self, kwargs):
        self.has_log('Starting moonlight mode for Yeelights')
        for e in config['entities']:
            self.call_service('yeelight/set_mode', entity_id=e, mode='moonlight')

    def timer_stop_cb(self, kwargs):
        self.has_log('Stoping moonlight mode for Yeelights')
        for e in config['entities']:
            self.turn_off(e)
