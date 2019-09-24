sensors = {
        # example occupancy sensor data
        'binary_sensor.some_occupancy_sensor': {
            'zone': 'somezone',
            'illuminance_sensor': 'sensor.some_illuminance_sensor',
            'enabling_boolean': 'input_boolean.some_enabling_boolean',
            'min_illuminance': 20000,  # TODO: make this configurable on the UI
            # Must be registered on lights.py!
            'light': 'light.somelight_to_turn_on',
            # Used for triggering an alert in away mode
            'is_outside': True,
            },
        }
