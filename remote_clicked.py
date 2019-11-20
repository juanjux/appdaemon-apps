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
            # Toggle lights, checking the state before
            if light.state == 'on':
                light.turn_off()
            else:
                light.turn_on()

        elif new == 'on':
            # Brightness up, turn_on
            light.turn_on()

        elif new.startswith('on_specific_'):
            # Turn on specific light
            l = '_'.join(new.split('_')[2:])
            sp = self.get_app('lights').get_light(l)
            sp.turn_on()

        elif new == 'off':
            # Brightness down, turn_off
            light.turn_off()

        elif new.startswith('off_specific_'):
            # Turn off specific light
            l = '_'.join(new.split('_')[2:])
            sp = self.get_app('lights').get_light(l)
            sp.turn_off()

        elif new == 'temp_fw':
            color_temp = light.attribute('color_temp')
            if color_temp is None:
                # chaeapo bulb
                return

            light.turn_on(color_temp=color_utils.cycle_temp_front(color_temp))

        elif new == 'temp_bw':
            color_temp = light.attribute('color_temp')
            if color_temp is None:
                # chaeapo bulb
                return
            light.turn_on(color_temp=color_utils.cycle_temp_back(color_temp))

        elif new.startswith('color_'):
            c = new.split('_')[1]
            light.turn_on(color_name=c, brightness_pct=100)

        elif new.startswith('temp_mireds_'):
            c = new.split('_')[2]
            light.turn_on(color_temp=c)

        elif new == 'rgb_fw':
            next_color = color_utils.cycle_color_front(light.last_nonwhite_color)
            light.turn_on(rgb_color=next_color)

        elif new == 'rgb_bw':
            prev_color = color_utils.cycle_color_back(light.last_nonwhite_color)
            light.turn_on(rgb_color=prev_color)

        else:
            return
