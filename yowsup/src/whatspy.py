import sys, os, time, shutil, argparse

import Image

from Yowsup.connectionmanager import YowsupConnectionManager
from Yowsup.Common.debugger import Debugger

USERNAME = '972583340860'
PASSWORD = 'jag6FSF6MicZmp9M8lrsSqoXYo8='.decode('base64')

phase = None
cm = None
signals_interface = None
methods_interface = None
args = None

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
def cb_presence_updated(jid, last_seen):
    print 'Last seen @', time.ctime(time.time() - last_seen)

def cb_presence_updated_batch(jid, last_seen):
    now = time.time()
    last = time.time() - last_seen
    print 'Last seen @', time.ctime(time.time() - last_seen)

    
def cb_presence_updated_once(jid, last_seen):
    ''' TODO: save the time to something and then use the web app to load it'''
    global time_got
    print 'HELLo'
    print 'Last seen @', time.ctime(time.time() - last_seen)
    time_got = True
    
# Contacts
def cb_contact_gotProfilePicture_once(jid, picture_id, image_path):
    ''' for eric to use for web app
    TODO: modify the path so that it goes to where you want
    TODO: modify a global variable so it knows its done'''
    global photo_got
    phone_number = jid.split('@')[0]
    print 'Got', phone_number
    # shutil.copyfile(image_path, os.path.join(args.t, phone_number + '.jpg'))
    photo_got = True

def cb_contact_gotProfilePicture_interactive(jid, picture_id, image_path):
    image = Image.open(image_path)
    image.show()

def cb_contact_gotProfilePicture_batch(jid, picture_id, image_path):
    phone_number = jid.split('@')[0]
    print 'Got', phone_number
    shutil.copyfile(image_path, os.path.join(args.t, phone_number + '.jpg'))

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

def batch(phone_numbers_path, profiles_picture_path):
    signals_interface.registerListener('presence_updated', cb_presence_updated_batch)
    
    with open(phone_numbers_path, 'rb') as f:
        phone_numbers = f.read().split('\n')
        
    if not os.path.exists(profiles_picture_path):
        os.mkdir(profiles_picture_path)

    for number_name in phone_numbers:
        phone_number, name = number_name.split(' ')
        jid = phone_number2jid(phone_number)

        print 'Request', phone_number
        methods_interface.call('contact_getProfilePicture', (jid,))
        time.sleep(2)

    time.sleep(10)

def get_photo_time(phone_number):
    ''' phone number includes the country code
    '''
    global photo_got, time_got
    setup()
    login()
    photo_got = False
    time_got = False
    while phase is None:
        time.sleep(0.5)

    signals_interface.registerListener('contact_gotProfilePicture', cb_contact_gotProfilePicture_once)
    signals_interface.registerListener('presence_updated', cb_presence_updated_once)

    jid = phone_number2jid(phone_number)
    methods_interface.call('presence_request', (jid,))

    methods_interface.call('contact_getProfilePicture', (jid,))
    
    while not (photo_got and time_got):
        #TODO: Time out the request for both photo and time depending on whats available
        print photo_got, time_got
        time.sleep(0.5)
            
    methods_interface.call('disconnect', ('closed!',))
        
def interactive():
    signals_interface.registerListener('presence_updated', cb_presence_updated)
    signals_interface.registerListener('contact_gotProfilePicture', cb_contact_gotProfilePicture_once)
    
    try:
        while True:
            cmd = raw_input('>>> ')
            
            if cmd == 'exit':
                break

            elif cmd.isdigit():
                jid = phone_number2jid(cmd)
                methods_interface.call('presence_request', (jid,))
                methods_interface.call('contact_getProfilePicture', (jid,))

            elif cmd == '':
                continue
                
            else:
                print 'Not a valid number...'

            time.sleep(2)

    except KeyboardInterrupt:
        print



setup()
login()

while phase is None:
    time.sleep(0.5)

p = 'numbers.txt'
if phase:
    batch(p)
    
methods_interface.call('disconnect', ('closed!',))
