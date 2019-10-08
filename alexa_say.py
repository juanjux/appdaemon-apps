from base_app import BaseApp
from local_config import alexa_say as config


class AlexaSay(BaseApp):
    """
    Makes Alexa talk the text from a UI text component
    """

    def initialize(self):
        self.listen_state(self.wrotten, config['text_input'])

    def wrotten(self, entity, attribute, old, new, kwargs):
        msg = self.get_state(config['text_input'])
        if not msg.strip():
            return

        self.smart_notify(config['notifiers'], msg)
