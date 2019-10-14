from base_app import BaseApp
from local_config import going_out as config


class GoingOut(BaseApp):
    def initialize(self):
        self.listen_state(self.going_out, config['boolean_activate'])

    def going_out(self, entity, attribute, old, new, kwargs):
        if old == new:
            return

        if new == 'on':
            self.start_going_out()
        else:
            self.returned()

    def start_going_out(self):
        # Open the configured doors
        self.open_doors()

        # Turn off all lights
        for light in self.get_app('lights').lights:
            self.turn_off(light)

        # Turn on the lights in config['out_lights_on'] for 5 minutes
        for lo in config['out_lights_on']:
            self.turn_on(lo)
        self.run_in(self.lights_off_cb, config['turned_on_lights_timeout'])

        # Turn on the door opening alarm in 30 seconds
        self.run_in(self.door_alarm_cb, config['turn_on_alarm_timeout'])

        self.smart_notify(config['bye_notifiers'], config['bye_msg'])

    def returned(self):
        # Disable the door opening alarm
        self.turn_off(config['boolean_alarm'])

        # Open the configured doors
        self.open_doors()

        # Turn on the light in config['back_lights_on']
        for lo in config['back_lights_on']:
            self.turn_on(lo)

    def open_doors(self):
        for to in config['open_doors']:
            st = self.get_state(to['entity'])
            if st == 'closed':
                self.log('Opening door {}'.format(to['entity']))
                self.call_service(to['open_service'], entity_id=to['entity'])

    def lights_off_cb(self, kwargs):
        for lo in config['out_lights_on']:
            self.turn_off(lo)

    def door_alarm_cb(self, kwargs):
        self.turn_on(config['boolean_alarm'])
