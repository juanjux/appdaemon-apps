from has_logging_app import HASLoggingApp


class AlexaSay(HASLoggingApp):
    """
    Makes Alexa talk
    """
    def initialize(self):
        self.listen_state(self.wrotten, 'input_text')

    def wrotten(self, entity, attribute, old, new, kwargs):
        msg = self.get_state('input_text.alexa_says')
        if not msg.strip():
            return

        self.call_service('notify/some_alexa_device',
                message=msg, data={'type': 'tts'})
