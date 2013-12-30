import threading
import Queue
import time

from Yowsup.connectionmanager import YowsupConnectionManager
from Yowsup.Common.debugger import Debugger

USERNAME = '972583340860'
PASSWORD = 'jag6FSF6MicZmp9M8lrsSqoXYo8='.decode('base64')
PRESENCE_WAIT = 60

Debugger.enabled = False

class WhatsappClient(threading.Thread):
    def __init__(self):
        super(WhatsappClient, self).__init__()

        self._exit = False

        self._connection_manger = YowsupConnectionManager()

        self._connection_manger.setAutoPong(True)

        self._signals_interface = self._connection_manger.getSignalsInterface()
        self._methods_interface = self._connection_manger.getMethodsInterface()

        self._signals_interface.registerListener('auth_success', self._cb_auth_success)
        self._signals_interface.registerListener('auth_fail', self._cb_auth_fail)
        self._signals_interface.registerListener('message_received', self._cb_message_received)
        self._signals_interface.registerListener('disconnected', self._cb_disconnected)
        self._signals_interface.registerListener('receipt_messageSent', self._cb_message_sent)
        self._signals_interface.registerListener('receipt_messageDelivered', self._cb_message_delivered)
        self._signals_interface.registerListener('image_received', self._cb_image_received)
        self._signals_interface.registerListener('video_received', self._cb_video_received)
        self._signals_interface.registerListener('audio_received', self._cb_audio_received)
        self._signals_interface.registerListener('location_received', self._cb_location_received)
        self._signals_interface.registerListener('vcard_received', self._cb_vcard_received)

        self._presence_thread = threading.Thread(target=self._method_presence_send_available)
        self._presence_thread.daemon = True

        self.incoming = Queue.Queue()
        self.outgoing = Queue.Queue()

    def _method_presence_send_available(self):
        while not self._exit:
            self._methods_interface.call('presence_sendAvailable')
            time.sleep(PRESENCE_WAIT)

    def _cb_auth_success(self, username):
        self._methods_interface.call('ready')
        self._presence_thread.start()
        self._handle_outgoing_loop()

    def _cb_auth_fail(self, username, reason):
        pass

    def _cb_disconnected(self, reason):
        self._exit = True

    def _cb_message_received(self, message_id, jid, message_content, timestamp, wants_receipt, push_name, is_broadcast):

        self.incoming.put((jid, timestamp, message_content))

        if wants_receipt:
            self._methods_interface.call('message_ack', (jid, message_id))
    
    
    def _cb_image_received(self, message_id, jid, preview, url, size, receipt_requested, _):
        if receipt_requested:
            self._methods_interface.call('message_ack', (jid, message_id))


    def _cb_video_received(self, message_id, jid, preview, url, size, receipt_requested, _):
        if receipt_requested:
            self._methods_interface.call('message_ack', (jid, message_id))

    def _cb_audio_received(self, message_id, jid, url, size, receipt_requested, _):
        if receipt_requested:
            self._methods_interface.call('message_ack', (jid, message_id))

    def _cb_location_received(self, message_id, jid, name, preview, latitude, longitude, receipt_requested, _):
        if receipt_requested:
            self._methods_interface.call('message_ack', (jid, message_id))

    def _cb_vcard_received(self, message_id, jid, name, data, receipt_requested, _):
        if receipt_requested:
            self._methods_interface.call('message_ack', (jid, message_id))

    def _cb_message_delivered(self, jid, message_id):
        self._methods_interface.call('delivered_ack', (jid, message_id))

    def _cb_message_sent(self, jid, message_id):
        pass

    def _handle_outgoing_loop(self):
        while not self._exit:
            jid, message_content = self.outgoing.get()
            self._methods_interface.call('message_send', (jid, message_content))

    def _login(self):
        self._methods_interface.call('auth_login', (USERNAME, PASSWORD))

    def get_queues(self):
        return self.incoming, self.outgoing

    def run(self):
        self._login()