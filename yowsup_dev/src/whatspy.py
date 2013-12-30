import sys, os, time, shutil, argparse

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

def write_available(phone_number, pull_time, last_online):
    f = open(phone_number + '.data', 'a')
    f.write(str(pull_time) + ',' + str(last_online) + '\n')
    f.close()
    
def cb_presence_updated_batch(jid, last_seen):
    now = time.time()
    last = time.time() - last_seen
    phone_number = jid.split('@')[0]
    write_available(phone_number, now, last)
    
    
# Contacts

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
    
def batch(phone_numbers_path):
    signals_interface.registerListener('presence_updated', cb_presence_updated_batch)
    with open(phone_numbers_path, 'rb') as f:
        phone_numbers = f.read().split('\n')

    for number_name in phone_numbers:
        try:
            phone_number, name = number_name.split(' ')
            jid = phone_number2jid(phone_number)

            print 'Request', phone_number, name
            methods_interface.call('presence_request', (jid,))
        except:
            print 'error on', number_name
        time.sleep(2)

setup()
login()

while phase is None:
    time.sleep(0.5)

p = 'numbers.txt'
if phase:
    batch(p)
    
methods_interface.call('disconnect', ('closed!',))
