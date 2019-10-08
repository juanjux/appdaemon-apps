# My app-daemon stuff

These are the apps I'm using on my Home Assistant + App Daemon. I'm publishing
them in case those can be useful directly or as reference to others.

All the configuration used by the apps is separated to the `local_config.py`
file. A commented example is provided in the file `local_config.py.example`; 
edit it and rename to the above should get you working once the requisites are
completed.

## Requisites

This uses some HAS `input_boolean` and `input_text` switches to enable/disable
or activate the apps and automations. Explaining how to add those is outside
the scope of this README, but the ones currently in use in the provided `apps.yaml` 
file are:

- `input_boolean.frontgate_warning`: enables/disables the `dooropen_warning`
  app.
- `input_boolean.doors_alarm`: enables/disables the door aperture alarm (so you
can switch it on HAS UI or programatically for example when you're out).
- `input_boolean.outside_movement_alarm`: same for the alarm implemented in the
`occupancy_alarm` app that will trigger if movement is detected outside the
house.

## Apps

### Lights

This is more a container/library for the lights than an app itself. Used by
other apps. 

### GotoSleep

When the `input_boolean` is enabled it turn off lights, triggering of outside
motion lights by occupancy sensors and turn on the outside alarms.

### Occupancy

Manages all the relation between occupancy (movement) sensors and the linked
lights. It has some aditional features:

- It won't turn off any light that is turned on by other means (remote, HAS UI, 
Alexa, et cetera).
- If a light is turned off manually, it won't turn it on for 10 (default)
  seconds so you can exit the room without triggering the lights again.
- You can use several occupancy sensors linked to the same light (as defined
in `local_config.py/occupancy['sensors'][sensor_name]['light']`) and it'll 
do the right thing.

### DoorOpenWarning

This is a periodic check that will call the configured notification if
a door is opened. Typically (as seen on the default `apps.yaml` file) this 
is useful to check if some outside doors are opened after a certain time
specified by the `time_constraint` setting in the `apps.yaml`, for example, 
garage or front gate doors that you don't want to be opened at night.

### DoorInstant

This provides an instant notification every time one of the configured 
doors opens or closes. I use it for my front gate so I know when somebody
is going or coming even before they connect/disconnect to the local wifi.

### DoorAlarm

Similar, but configured to produce a stronger notification (Pushover emergency
ackowleagable notification) every time it detects a door/window has opened. 
To be used as switchable alarm when going out or in vacation mode.

### OccupancyAlarm

Same as above, but triggered when an outside motion detector detects motion.

### RemoteClicked

This manages all the smart remotes and the lights they're linked to. It can be
configured for remotes of several different brands using different button
layouts and publishing varying status messages (example configs are provided for
Ikea's Tradfri, Philips and Xiaomi Aqara remotes).

### YeelightNightMode

This is a simple app that enables "moonlight mode" on the configured Yeelight
lights. I use it for my daughter bedside lamp and and some night lights on 
halls and bathrooms.

### AlexaSay

This will make Alexa say whatever is written in the configured HAS'
`input_text`. It needs the `alexa_media` integration configured on HAS.

### AlexaRepeat

Same, but repeated the `friendly_name` of any of the configured `input_boolean`
elements until the boolean is switched off. Useful for "dinner is ready" and
similar calls.

### RainSwitcher

Disable the configured switches (trough it can also work for lights, groups
or any other entity that can be switches off) when a water sensor detect waters.
I use this to automatically turn off some not-so-well-isolated outside lights
when there is rain. The switching off is done either by Sonoff Basic switches
or Xiaomi Aqara wall switches (the ones with neutral because they ones without 
doesn't really cut off the power!).

### LeakNotify

Same but it just provides a warning. Used for the sink leak detector.

### Arrival

Configurable notifications when some `device_tracker` arrives.

### GoingOut

Automation to enable when going outside. It:

- Opens the front gate if it's closed.
- Turns on some configurable lights for five minutes (for example your front door and garage lights).
- Turns off all other lights.
- After a minute, enable the door/occupancy alarms.
