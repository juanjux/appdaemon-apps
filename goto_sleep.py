import datetime

from has_logging_app import HASLoggingApp

import remotes
from occupancy_sensors import sensors as msensors


class GotoSleep(HASLoggingApp):
    def initialize(self):
        if self.get_state('input_boolean.goto_sleep') == 'on':
            self.timer = self.run_once(self.morning_start_cb, datetime.time(6, 0, 0))
        else:
            self.timer = None

        self.listen_state(self.clicked, 'input_boolean.goto_sleep')

    def clicked(self, entity, attribute, old, new, kwargs):
        if new == 'on':
            self.has_log('goto_sleep clicked, disabling lights and outside motion sensors')
            # turn off all lights until 06:00:00
            for r in remotes.remotes.values():
                self.turn_off(r['light'])

            # ditto with all motion sensors outside
            self.apply_motion_sensors(self.turn_off)
            # set a timer to enable the motion sensors again
            self.cancel_timer(self.timer)
            self.timer = self.run_once(self.morning_start_cb, datetime.time(6, 0, 0))
        else:
            # disabled, enable motion sensors again
            self.has_log('goto_sleep disabled, enabling outside motion sensors again')
            self.apply_motion_sensors(self.turn_on)
            self.cancel_timer(self.timer)
            self.timer = None

    def morning_start_cb(self, kwargs):
        self.has_log('Time to enable again outside movement sensors')
        self.apply_motion_sensors(self.turn_on)
        self.turn_off('input_boolean.goto_sleep')

    def apply_motion_sensors(self, cb):
        for data in msensors.values():
            if data['is_outside']:
                cb(data['enabling_boolean'])
