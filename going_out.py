from base_app import BaseApp
from local_config import going_out as config


class GoingOut(BaseApp):
    def initialize(self):
        self.listen_state(self.going_out, config['boolean_activate'])

    def going_out(self, entity, attribute, old, new, kwargs):
        if new == 'off':
            return

        # Open the front door
        for to in config['open_doors']:
            st = self.get_state(to['entity'])
            if st == 'closed':
                self.call_service(to['open_service'], entity_id=to['entity'])

        # Turn on the front stairs for 5 minutes
        for lo in config['lights_on']:
            self.turn_on(lo)
        self.run_in(self.lights_off_cb, 60 * 5)

        # Turn off all lights except the front stairs
        for light in self.get_app('lights').lights:
            if light not in config['lights_on']:
                self.turn_off(light)

        # Turn on the door opening alarm in 30 seconds
        self.run_in(self.door_alarm_cb, 30)

        self.smart_notify(config['bye_notifiers'], config['bye_msg'])

    def lights_off_cb(self, kwargs):
        for lo in config['lights_on']:
            self.turn_off(lo)

    def door_alarm_cb(self, kwargs):
        self.turn_on(config['boolean_alarm'])
