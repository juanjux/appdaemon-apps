import time

from base_app import BaseApp
from local_config import alexa_repeat as config


class AlexaRepeat(BaseApp):
    """
    Makes Alexa repeat the friendly name of the enabled boolean until
    stopped. Useful for "dinner is ready!" calls and such. It will listen
    for symbols in "ui_components" starting with the name "alexa_sayrepeat_".
    """

    def initialize(self):
        for boolean in config['booleans_activate']:
            self.listen_state(self.repeat, boolean)

    def repeat(self, entity, attribute, old, new, kwargs):
        text = ', '.join([self.friendly_name(entity)] * config['times_repeat'])

        while True:
            state = self.get_state(entity)
            if state != 'on':
                return

            self.smart_notify(config['notifiers'], text)
            # TODO: change to timer with a callback
            time.sleep(config['sleep_time'])
