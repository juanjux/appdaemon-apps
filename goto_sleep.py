from base_app import BaseApp
from occupancy_sensors import sensors as msensors
from local_config import goto_sleep as config


class GotoSleep(BaseApp):
    def initialize(self):
        if self.get_state(config['boolean_activate']) == 'on':
            self.timer = self.run_once(self.morning_start_cb, config['end_time'])
        else:
            self.timer = None

        self.listen_state(self.clicked, config['boolean_activate'])

    def clicked(self, entity, attribute, old, new, kwargs):
        if new == 'on':
            self.has_log('{} clicked, disabling lights and outside motion sensors'
                .format(config['boolean_activate']))
            # turn off all lights until END_TIME
            for light in self.get_app('lights').lights:
                self.turn_off(light)

            # ditto with all motion sensors outside
            self.apply_motion_sensors(self.turn_off)
            # set a timer to enable the motion sensors again
            self.cancel_timer(self.timer)
            self.timer = self.run_once(self.morning_start_cb, config['end_time'])
        else:
            # disabled, enable motion sensors again
            self.has_log('%s disabled, enabling outside motion sensors again'
                    .format(config['boolean_activate']))
            self.apply_motion_sensors(self.turn_on)
            self.cancel_timer(self.timer)
            self.timer = None

    def morning_start_cb(self, kwargs):
        self.has_log('Time to enable again outside movement sensors')
        self.apply_motion_sensors(self.turn_on)
        self.turn_off(config['boolean_activate'])

    def apply_motion_sensors(self, cb):
        for data in msensors.values():
            if data['is_outside']:
                cb(data['enabling_boolean'])
