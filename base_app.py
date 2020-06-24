import appdaemon.plugins.hass.hassapi as hass

import traceback

def escape_telegram(msg: str):
    return msg.replace('_', r'\_').replace('*', r'\*').replace('~', r'\~')

class BaseApp(hass.Hass):
    def has_log(self, message):
        """Logs to normal log and home assistant logbook"""
        self.log(message)
        self.call_service('logbook/log', name='AppDaemon Event', message=message)

    def smart_notify(self, notifiers, msg):
        if isinstance(notifiers, dict):
            notifiers = [notifiers]

        for n in notifiers:
            try:
                # FIXME: ugly, depends on the service name
                if '/telegram' in n['service']:
                    msg = escape_telegram(msg)

                if 'data' in n and n['data'] is not None:
                    self.call_service(n['service'], message=msg, data=n['data'])
                else:
                    self.call_service(n['service'], message=msg)
                self.log('Sending notification to {}: {}'.format(n['service'], msg))
            except Exception as e:
                self.log(traceback.format_exc())
