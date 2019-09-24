from has_logging_app import HASLoggingApp
from remotes import color_distance

import threading


class HolidayActivity:
    def __init__(self, start, delta):
        # TODO:
        # parse times (list of tuples with strings like ('21:00', '03:00'))
        # and convert to datetime.time and datetime.timedelta
        pass


class Light:
    """
    Encapsulates data and operation related to a light or light groups.
    Lights are instanced on the lights.py app which also have the dictionaries
    with all the lights data.
    """
    def __init__(self, app_ref, entity, grouping, occ_turnoff_timeout=65,
            manual_turnoff_timeout=15, holidays_turnon_times=None):
        self.app = app_ref
        self.entity = entity
        self.grouping = grouping
        self._group_entity = '{}.{}'.format(grouping, entity)
        self.occ_turnoff_timeout = occ_turnoff_timeout
        self.manual_turnoff_timeout = manual_turnoff_timeout
        self.lock = threading.Lock()

        # TODO: implement this
        self.holidays_turnon_times = []
        if holidays_turnon_times:
            for start, delta in holidays_turnon_times:
                self.holidays_turnon_times.append(HolidayActivity(start, delta))

        # Initial state
        self.occ_can_turnon = True
        self.occ_can_turnoff = True
        self.occ_turnoff_timer = None
        self.occ_can_turnon_timer = None
        self.last_nonwhite_color = None

    @property
    def group_entity(self):
        return self._group_entity

    def turn_on(self, **kwargs):
        self.app.log('Turning on {}'.format(self._group_entity))
        self.app.turn_on(self._group_entity, **kwargs)

        # If it's a color, store it for cycles
        if 'rgb_color' in kwargs:
            new_color = kwargs['rgb_color']
            # Check that is not white. Values differ a little so we check the
            # distance from the white color
            distance = color_distance(new_color, [255, 255, 255])
            if distance > 10:
                self.last_nonwhite_color = new_color

    def turn_off(self):
        self.app.turn_off(self._group_entity)

    def manual_turn_on(self, **kwargs):
        """
        Using a remote or (TODO) the HAS UI. Won't allow
        occupancy sensors to turn off the manually enabled light
        """
        with self.lock:
            self.occ_can_turnoff = False
            self.occ_can_turnon = True

        self.app.cancel_timer(self.occ_turnoff_timer)
        self.turn_on(**kwargs)

    def manual_turn_off(self):
        """
        Enable turn off from occupancy sensors again but allow occTurnOn()
        to turn the light for self.manual_turnoff_timeout seconds so the light isn't
        inmediately turned on again
        """

        with self.lock:
            self.occ_can_turnoff = True
            self.occ_can_turnon = False
            self.app.cancel_timer(self.occ_can_turnon_timer)
            self.occ_can_turnon_timer = self.app.run_in(self.enable_occ_can_turnon,
                    self.manual_turnoff_timeout)
        self.turn_off()

    def enable_occ_can_turnon(self, kwargs):
        with self.lock:
            self.occ_can_turnon = True

    def occ_turn_on(self, **kwargs):
        if not self.occ_can_turnon:
            self.app.log('Cant turn on {}, inside grace period from manual turn off'
                    .format(self._group_entity))
            return

        if self.occ_can_turnoff:
            self.turn_on(**kwargs)
            self.occ_turn_off_later()
        else:
            self.app.log('Cant set timer to turn off {} it was manually turned on'
                    .format(self._group_entity))

    def occ_turn_off_later(self):
        # Cancel previous timer
        if self.occ_turnoff_timer is not None:
            self.app.log('Reseting movement timer for {}'.format(self._group_entity))
            with self.lock:
                self.app.cancel_timer(self.occ_turnoff_timer)
                self.occ_turnoff_timer = None

        # Set a new one
        self.occ_turnoff_timer = self.app.run_in(self.occ_turn_off,
                self.occ_turnoff_timeout)

    def occ_turn_off(self, kwargs):
        if not self.occ_can_turnoff:
            self.app.log('Timeout expired for {} but'.format(self._group_entity) +
                'it seems it was manually turned on ...doing nothing')
            return

        self.app.log('Turning off {}, timeout expired'.format(self._group_entity))
        self.turn_off()

    @property
    def state(self):
        return self.app.get_state(self._group_entity)

    @property
    def color(self):
        return self.app.get_state(self._group_entity, attribute='rgb_color')

    def attribute(self, attribute):
        return self.app.get_state(self._group_entity, attribute=attribute)
