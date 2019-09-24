import threading

from has_logging_app import HASLoggingApp
from light import Light

DEFAULT_MANUAL_TURNOFF_TIMEOUT = 15

# Fill this with your lights, light groups, groups or switches
lights = {
        'somelight': {
            # grouping used (light, group, switch, et cetera).
            'grouping': 'light',
            # time for turning off after being turned on by an
            # occupancy sensor
            'occTurnOff': None,
            # time to turning on again after a manual turn off so the light
            # doesnt inmediately turn on
            'manualTurnOffTimeout': DEFAULT_MANUAL_TURNOFF_TIMEOUT,
            # TODO: time at which the light will turn on and off in holiday mode
            'holidayTimes': [],
            },
}


class LightsInitializer(HASLoggingApp):
    """
    Initialize the global lights list; needs to be an app
    to access self.global and create dependencies
    """
    def initialize(self):
        lock = threading.Lock()
        with lock:
            self.global_vars['lights'] = {}
            for entity, value in lights.items():
                l = Light(
                    app_ref = self,  # dirty, but needed so lights can call the (self.)API
                    entity = entity,
                    grouping = value['grouping'],
                    occ_turnoff_timeout = value['occTurnOff'],
                    manual_turnoff_timeout = value['manualTurnOffTimeout'],
                    holidays_turnon_times = value['holidayTimes']
                    )
                self.global_vars['lights'][l.group_entity] = l
