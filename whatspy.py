import sys, os, time, shutil

from Yowsup.connectionmanager import YowsupConnectionManager
from Yowsup.Common.debugger import Debugger
from config import USERNAME, PASSWORD

PHONE_PATH = 'static/phone_images/'
TIMEOUT_SECS = 5

def phone_number2jid(phone_number):
    return phone_number + '@s.whatsapp.net'
def image_location(phone_number):
    return os.path.join(PHONE_PATH, phone_number + '.jpg')

class Whatspy(object):
    phase = None
    cm = None
    signals_interface = None
    methods_interface = None
    time_got = None
    photo_got = None

    # Login
    def cb_auth_success(self, username):
        print 'Authed %s' % username
        self.methods_interface.call('ready')
        self.phase = True

    def cb_auth_fail(self, username, reason):
        print 'Auth Fail!', username, reason
        self.phase = False

    def login(self):
        self.methods_interface.call('auth_login', (USERNAME, PASSWORD))

    # Presence
    def cb_presence_updated_once(self, jid, last_seen):
        self.time_got = time.ctime(time.time() - last_seen)
        print 'Last seen @', self.time_got

    # Contacts
    def cb_contact_gotProfilePicture_once(self, jid, picture_id, image_path):
        phone_number = jid.split('@')[0]
        print 'Got', phone_number
        new_path = image_location(phone_number)
        shutil.copyfile(image_path, new_path)
        self.photo_got = new_path

    # Main
    def setup(self):
        #global cm, signals_interface, methods_interface

        Debugger.enabled = False

        self.cm = YowsupConnectionManager()

        self.cm.setAutoPong(True)

        self.signals_interface = self.cm.getSignalsInterface()
        self.methods_interface = self.cm.getMethodsInterface()

        self.signals_interface.registerListener('auth_success', self.cb_auth_success)
        self.signals_interface.registerListener('auth_fail', self.cb_auth_fail)

    def get_photo_time(self, phone_number):
        ''' phone number includes the country code'''
        self.setup()
        self.login()
        self.photo_got = None
        self.time_got = None
        while self.phase is None:
            time.sleep(0.5)

        self.signals_interface.registerListener('presence_updated', self.cb_presence_updated_once)

        jid = phone_number2jid(phone_number)
        self.methods_interface.call('presence_request', (jid,))

        # only get image if doesn't already exist
        if os.path.isfile(image_location(phone_number)):
          self.photo_got = image_location(phone_number)
        else:
          self.signals_interface.registerListener('contact_gotProfilePicture', self.cb_contact_gotProfilePicture_once)
          self.methods_interface.call('contact_getProfilePicture', (jid,))

        timeout = 0
        while not (self.photo_got and self.time_got) and timeout < TIMEOUT_SECS:
            time.sleep(0.25)
            timeout += 0.25

        return (self.photo_got, self.time_got)
