import sys, os, time, shutil

from Yowsup.connectionmanager import YowsupConnectionManager
from Yowsup.Common.debugger import Debugger

USERNAME = '972583340860'
PASSWORD = 'jag6FSF6MicZmp9M8lrsSqoXYo8='.decode('base64')

phase = None
cm = None
signals_interface = None
methods_interface = None

# Utils
def phone_number2jid(phone_number):
    return phone_number + '@s.whatsapp.net'

# Login

def cb_auth_success(username):
    global phase
    print 'Authed %s' % username
    methods_interface.call('ready')
    phase = True

def cb_auth_fail(username, reason):
    global phase
    print 'Auth Fail!', username, reason
    phase = False

def login():
    methods_interface.call('auth_login', (USERNAME, PASSWORD))

# Presence
def cb_presence_updated_once(jid, last_seen):
    ''' TODO: save the time to something and then use the web app to load it'''
    global time_got
    time_got = time.ctime(time.time() - last_seen)
    print 'Last seen @', time_got

# Contacts
def cb_contact_gotProfilePicture_once(jid, picture_id, image_path):
    ''' for eric to use for web app
    TODO: modify the path so that it goes to where you want
    '''
    global photo_got
    phone_number = jid.split('@')[0]
    print 'Got', phone_number
    shutil.copyfile(image_path, os.path.join(args.t, phone_number + '.jpg'))
    photo_got = True # set photo to this

# Misc
def cb_disconnected(reason):
        print 'Disconnected because %s' % reason
        sys.exit(0)

# Main

def setup():

    global cm, signals_interface, methods_interface

    Debugger.enabled = False

    cm = YowsupConnectionManager()

    cm.setAutoPong(True)

    signals_interface = cm.getSignalsInterface()
    methods_interface = cm.getMethodsInterface()

    signals_interface.registerListener('auth_success', cb_auth_success)
    signals_interface.registerListener('auth_fail', cb_auth_fail)
    signals_interface.registerListener('disconnected', cb_disconnected)

def get_photo_time(phone_number):
    ''' phone number includes the country code
    '''
    global photo_got, time_got
    setup()
    login()
    photo_got = None
    time_got = None
    while phase is None:
        time.sleep(0.5)

    signals_interface.registerListener('contact_gotProfilePicture', cb_contact_gotProfilePicture_once)
    signals_interface.registerListener('presence_updated', cb_presence_updated_once)

    jid = phone_number2jid(phone_number)
    methods_interface.call('presence_request', (jid,))

    methods_interface.call('contact_getProfilePicture', (jid,))
    
    timeout = 0
    while not (photo_got and time_got) and timeout < 1:
        print photo_got, time_got
        time.sleep(0.25)
        timeout += 0.25

#    methods_interface.call('disconnect', ('closed!',))
    return (photo_got, time_got)

print get_photo_time('16094755004')
print get_photo_time('16094755004')
