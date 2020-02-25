from copy import deepcopy

from base_app import BaseApp
from local_config import watering as config


def bool2num(boolstr):
    if boolstr.lower() == 'on':
        return 1
    return 0


class Watering(BaseApp):
    def initialize(self):
        # Check the several input widgets on HAS GUI and update
        # the Sonoffs controlling the watering zones

        to_monitor = list(config['zone_enablers'].values()) +\
                list(config['start_time_inputs'].values()) +\
                list(config['weekday_enablers'].values()) +\
                [config['watering_duration_input']]

        for m in to_monitor:
            self.listen_state(self.update_watering, m)

    def update_watering(self, entity, attribute, old, new, kwargs):
        """
        Read all the various input widgets on HAS guy (see local_config for
        the mappings) and update the timers on zone_controllers which are expected
        to be things running Tasmota and reachable via MQTT
        """

        # Get the common values for all zones
        update_dict = {
                "Repeat": 1,  # Needs to be enabled or will do only once
                "Mode": 0,  # Use clock time
                "Action": 1,  # Turn relay on (PulseTime will turn it off)
        }

        # Watering duration
        try:
            update_dict['duration'] = \
                    int(self.get_state(config['watering_duration_input']))
        except ValueError:
            update_dict['duration'] = 0

        # Days of the week
        update_dict['Days'] = ''.join([
                str(bool2num(self.get_state(config['weekday_enablers'][day])))
                for day in ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
                'friday', 'saturday')
                ])

        for zone in config['zone_controllers'].keys():
            self.update_zone_config(zone, deepcopy(update_dict))

    def update_zone_config(self, zone, update_dict):
        # Enabled state
        update_dict['Arm'] = bool2num(self.get_state(config['zone_enablers'][zone]))

        # Watering start time
        update_dict['Time'] = self.get_state(config['start_time_inputs'][zone])[:-3]

        self.call_mqtt(zone, update_dict)

    def call_mqtt(self, zone, update_dict):
        """
        Do MQTT calls to update PulseTime and Timer1
        """
        srv = "mqtt/publish"
        base_topic = config['zone_controllers'][zone] + '/cmnd/'

        # Update PulseTimer (watering duration) first (time = 100 + seconds)
        self.call_service(srv, topic = base_topic + 'PulseTime',
                payload = 100 + (update_dict['duration'] * 60))

        # Enable the "Enable Timers" checkbox
        self.call_service(srv, topic = base_topic + "Timers", payload = 1)

        # Remove the duration and update the Timer1
        del update_dict['duration']
        self.call_service(srv, topic = base_topic + 'Timer1',
                payload = str(update_dict))
        self.log(zone + ": " + str(update_dict))
