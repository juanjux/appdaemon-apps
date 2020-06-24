from base_app import BaseApp

import color_utils
from local_config import remote_clicked as config


class RemoteClicked(BaseApp):
    def initialize(self):
        for remote in config['remotes']:
            self.listen_state(self.clicked, remote)

        # Used to ignore the next "on" signal for linked lights. This is needed because
        # some switch "A" that also turn on other switch "B" could enter into a loop once
        # "B" sends its "on" signal if that's processed here and has "A" as a linked
        # light.  So what we do is that when "A" "on" signal is processed, it turns on "B"
        # but adds "B" to ignore_linkedsignal. Then when "B" sents his "on" signal, it will
        # be ignored and removed from "ignore_linkedsignal". Also, things in this list will
        # be removed by a timer 2 seconds after being added to avoid a possible problem
        # caused by "B" "on" signal not arriving and the next (correct, manually issued)
        # "on" signal from B being ignored. What is stored is entity__state, e.g.:
        # light.kitchen__on (the state is also stored so in a turn on followed by a quick
        # turn off the later is not ignored).
        self.ignore_linkedsignal = set()

    def clicked(self, entity, attribute, old, new, kwargs):
        linkedstr = '%s__%s' % (entity, new)
        if linkedstr in self.ignore_linkedsignal:
            try:
                self.ignore_linkedsignal.remove(linkedstr)
            except KeyError:
                # Probably removed right now by the callback
                pass
            self.log('Ignored linked light {} signal'.format(entity))
            return

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

        # See above about treatment of "linked" vs normal "light"
        if 'linked' in r:
            # Add ourselves too so the virtual light/group/switch toggling
            # the group doesnt toggle this device too
            r['linked'].append(entity)

            for l in r['linked']:
                linkedstr = '%s__%s' % (l, new)
                self.ignore_linkedsignal.add(linkedstr)
                self.run_in(self.linked_remove_cb, 2, light=linkedstr)

        # In the future this will support more than one light, thus the list and loop
        for l in [r['light']]:
            light = self.get_app('lights').get_light(l)
            new = buttons[new]
            self.has_log('Remote {}: {}'.format(entity, new))

            if new == 'toggle':
                # Toggle lights, checking the state before
                light.turn_off() if light.state == 'on' else light.turn_on()

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
                    continue

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

    def linked_remove_cb(self, kwargs):
        light = kwargs['light']
        try:
            self.ignore_linkedsignal.remove(light)
        except KeyError:
            # Removed at signal receive or by other callback
            pass
