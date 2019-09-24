import datetime

from has_logging_app import HASLoggingApp


class NightModeLamp(HASLoggingApp):
    def initialize(self):
        # TODO: configure in the UI
        self.start = datetime.time(21, 30, 00)
        self.stop = datetime.time(8, 0, 0)
        if self.get_state('input_boolean.nightmode_lamp') == 'on':
            self.start_timers()
        self.listen_state(self.clicked, 'input_boolean.nightmode_lamp')

    def clicked(self, entity, attribute, old, new, kwargs):
        self.cancel_timers()

        if new == 'on':
            # Ensure the timer is updated in case we changed the dates
            self.start_timers()

    def start_timers(self):
        self.timer_start = self.run_daily(self.timer_start_cb, self.start)
        self.timer_stop = self.run_daily(self.timer_stop_cb, self.stop)

    def cancel_timers(self):
        self.cancel_timer(self.timer_start)
        self.timer_start = None

        self.cancel_timer(self.timer_stop)
        self.timer_stop = None

    def timer_start_cb(self, kwargs):
        self.has_log('Starting moonlight mode for bedside lamp')
        self.call_service('yeelight/set_mode', entity_id='light.bedside_lamp', mode='moonlight')

    def timer_stop_cb(self, kwargs):
        self.has_log('Stoping moonlight mode for bedside lamp')
        self.turn_off('light.bedside_lamp')
