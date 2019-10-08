from base_app import BaseApp

import color_utils
from local_config import remote_clicked as config


class RemoteClicked(BaseApp):
    def initialize(self):
        for remote in config['remotes']:
            self.listen_state(self.clicked, remote)

    def clicked(self, entity, attribute, old, new, kwargs):
        if old == new or not new:
            # tradfri remotes send two events '' -> 'toggle' and
            # 'toggle' -> 'toggle' for some reason
            return

        r = config['remotes'][entity]
        buttons = config['remote_mappings'][r['buttons']]
        if new not in buttons:
            self.log('Warning: unknown button "{}" pressed on remote {}'
                    .format(new, entity))
            return

        light = self.get_app('lights').get_light(r['light'])
        new = buttons[new]
        self.has_log('Remote {}: {}'.format(entity, new))

        if new == 'toggle':
            # Central button, toggle lights
            if light.state == 'on':
                light.turn_off()
            else:
                light.turn_on()

        elif new == 'on':
            # Brightness up, turn_on
            light.turn_on()

        elif new == 'off':
            # Brightness down, turn_off
            light.turn_off()

        elif new == 'color_temp_fw':
            color_temp = light.attribute('color_temp')
            if color_temp is None:
                # chaeapo bulb
                return

            light.turn_on(color_temp=color_utils.cycle_temp_front(color_temp))

        elif new == 'color_temp_bw':
            color_temp = light.attribute('color_temp')
            if color_temp is None:
                # chaeapo bulb
                return
            light.turn_on(color_temp=color_utils.cycle_temp_back(color_temp))

        elif new == 'color_white':
            light.turn_on(color_name='white')

        elif new == 'color_rgb_fw':
            next_color = color_utils.cycle_color_front(light.last_nonwhite_color)
            light.turn_on(rgb_color=next_color)
        else:
            return
