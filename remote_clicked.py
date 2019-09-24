from has_logging_app import HASLoggingApp

import remotes


class RemoteClicked(HASLoggingApp):
    """
    Manages remotes. Those are defined in the remote.py module.
    """
    def initialize(self):
        for remote in remotes.remotes:
            self.listen_state(self.clicked, remote)

    def clicked(self, entity, attribute, old, new, kwargs):
        if old == new or not new:
            # tradfri remotes send two events '' -> 'toggle' and
            # 'toggle' -> 'toggle' for some reason
            return
        r = remotes.remotes[entity]
        if new not in r['buttons']:
            self.log('Warning: unknown button "{}" pressed on remote {}'
                    .format(new, entity))
            return

        light = self.global_vars['lights'][r['light']]
        new = r['buttons'][new]
        self.has_log('mando {} {}'.format(entity, new))

        if new == 'toggle':
            # Central button, toggle lights
            if light.state == 'on':
                light.manual_turn_off()
            else:
                light.manual_turn_on()

        elif new == 'on':
            # Brightness up, manual_turn_on
            light.manual_turn_on()

        elif new == 'off':
            # Brightness down, manual_turn_off
            light.manual_turn_off()

        elif new == 'color_temp_fw':
            color_temp = light.attribute('color_temp')
            if color_temp is None:
                # chaeapo bulb
                return

            light.manual_turn_on(color_temp=remotes.cycle_temp_front(color_temp))

        elif new == 'color_temp_bw':
            color_temp = light.attribute('color_temp')
            if color_temp is None:
                # chaeapo bulb
                return
            light.manual_turn_on(color_temp=remotes.cycle_temp_back(color_temp))

        elif new == 'color_white':
            light.manual_turn_on(color_name='white')

        elif new == 'color_rgb_fw':
            next_color = remotes.cycle_color_front(light.last_nonwhite_color)
            light.manual_turn_on(rgb_color=next_color)
        else:
            return
