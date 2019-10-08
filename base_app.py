import appdaemon.plugins.hass.hassapi as hass


class BaseApp(hass.Hass):
    def has_log(self, message):
        """Logs to normal log and home assistant logbook"""
        self.log(message)
        self.call_service('logbook/log', name='AppDaemon Event', message=message)

    def smart_notify(self, notifiers, msg):
        if isinstance(notifiers, dict):
            notifiers = [notifiers]

        for n in notifiers:
            if 'data' in n and n['data'] is not None:
                self.call_service(n['service'], message=msg, data=n['data'])
            else:
                self.call_service(n['service'], message=msg)
