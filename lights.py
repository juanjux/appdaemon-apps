from base_app import BaseApp
from local_config import lights as config
from color_utils import color_distance


class Lights(BaseApp):
    """
    Initializes all lights. This is mostly a container of Light objects
    which will be used by other apps
    """
    def initialize(self):
        self.lights = {}
        for entity, value in config['definitions'].items():
            l = Light(
                app_ref = self,  # dirty, but needed so lights can call the (self.)API
                entity = entity,
                grouping = value['grouping'],
                occ_turnoff_timeout = value['occTurnOff'],
                manual_turnoff_timeout = value['manualTurnOffTimeout'],
                holidays_turnon_times = value['holidayTimes']
                )
            self.lights[l.group_entity] = l

    def get_light(self, group_entity):
        return self.lights[group_entity]


class HolidayActivity:
    def __init__(self, start, delta):
        # TODO:
        # parse times (list of tuples with strings like ('21:00', '03:00'))
        # and convert to datetime.time and datetime.timedelta
        pass


class Light:
    def __init__(self, app_ref, entity, grouping, occ_turnoff_timeout=65,
            manual_turnoff_timeout=15, holidays_turnon_times=None):
        self.app = app_ref
        self.entity = entity
        self.grouping = grouping
        self._group_entity = '{}.{}'.format(grouping, entity)
        self.occ_turnoff_timeout = occ_turnoff_timeout
        self.manual_turnoff_timeout = manual_turnoff_timeout

        # TODO: implement this
        self.holidays_turnon_times = []
        if holidays_turnon_times:
            for start, delta in holidays_turnon_times:
                self.holidays_turnon_times.append(HolidayActivity(start, delta))

        # Initial state
        self.turned_on_from_occ = False
        self.turned_off_from_occ = False

        self.occ_can_turnon = True
        self.occ_can_turnoff = True

        self.occ_turnoff_timer = None
        self.occ_can_turnon_timer = None

        self.last_nonwhite_color = None

        self.app.listen_state(self.turned_off, self._group_entity)
        self.app.listen_state(self.turned_on, self._group_entity)

    def turned_on(self, entity, attribute, old, new, kwargs):
        if old != new and new == 'on':
            # no need for the dont-turn-on occ grace period anymore

            if self.turned_on_from_occ:
                self.turned_on_from_occ = False
                self.app.log('{} turned on automatically'.format(self._group_entity))
            else:
                # turned on manually, dont let occ sensors turn it off
                self.app.cancel_timer(self.occ_turnoff_timer)
                self.occ_turnoff_timer = None
                self.occ_can_turnoff = False
                self.app.log('{} turned on manually'.format(self._group_entity))

    def turned_off(self, entity, attribute, old, new, kwargs):
        if old != new and new == 'off':
            self.occ_can_turnoff = True

            if self.turned_off_from_occ:
                self.turned_off_from_occ = False
                self.app.log('{} turned off automatically'.format(self._group_entity))
            else:
                # turned off manually, don't allow occ sensors to turn on
                # the lights for manual_turnoff_timeout seconds (grace period
                # to exit the room)
                self.app.log('{} turned off manually'.format(self._group_entity))
                self.occ_can_turnon = False
                self.app.cancel_timer(self.occ_can_turnon_timer)
                self.occ_can_turnon_timer = self.app.run_in(
                        self.enable_occ_can_turnon_cb,
                        self.manual_turnoff_timeout
                )

    def turn_off(self):
        self.app.turn_off(self._group_entity)

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

    def enable_occ_can_turnon_cb(self, kwargs):
        self.occ_can_turnon_timer = None
        self.occ_can_turnon = True

    def enable_occ_can_turnoff_cb(self, kwargs):
        self.occ_can_turnoff = True

    def occ_turn_on(self, **kwargs):
        if not self.occ_can_turnon:
            self.app.log('Not turning on {}, was turned off by hand recently'
                    .format(self._group_entity))
            return

        if self.occ_can_turnoff:
            self.turned_on_from_occ = True
            self.turn_on(**kwargs)
            self.occ_turn_off_later()
        else:
            self.app.log('Occupancy ignoring {}, it was manually turned on'
                    .format(self._group_entity))

    def occ_turn_off_later(self):
        # Cancel previous timer
        if self.occ_turnoff_timer is not None:
            self.app.log('Reseting occupancy timer for {}'.format(self._group_entity))
            self.app.cancel_timer(self.occ_turnoff_timer)
            self.occ_turnoff_timer = None

        # Set a new one
        self.occ_turnoff_timer = self.app.run_in(self.occ_turn_off_cb,
                self.occ_turnoff_timeout)

    def occ_turn_off_cb(self, kwargs):
        self.occ_turnoff_timer = None
        if not self.occ_can_turnoff:
            self.app.log('Timeout expired for {} but'.format(self._group_entity) +
                'it seems it was manually turned on ...doing nothing')
            return

        self.app.log('Turning off {}, timeout expired'.format(self._group_entity))
        self.turned_off_from_occ = True
        self.turn_off()

    @property
    def state(self):
        return self.app.get_state(self._group_entity)

    @property
    def color(self):
        return self.app.get_state(self._group_entity, attribute='rgb_color')

    def attribute(self, attribute):
        return self.app.get_state(self._group_entity, attribute=attribute)
