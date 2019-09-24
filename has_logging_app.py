import appdaemon.plugins.hass.hassapi as hass


class HASLoggingApp(hass.Hass):
    def has_log(self, message):
        """Logs to normal log and home assistant logbook"""
        self.log(message)
        self.call_service('logbook/log', name='AppDaemon Event', message=message)
