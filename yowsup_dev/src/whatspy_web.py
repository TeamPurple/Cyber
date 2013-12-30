############
# Whatsapp #
############

import time

from Yowsup.connectionmanager import YowsupConnectionManager
from Yowsup.Common.debugger import Debugger

USERNAME = '972583340860'
PASSWORD = 'jag6FSF6MicZmp9M8lrsSqoXYo8='.decode('base64')

DEBUG_JID = '13104874553@s.whatsapp.net'

phase = None
cm = None
signals_interface = None
methods_interface = None
profile_picture_path = None

# Utils

def phone_number2jid(phone_number):
    return phone_number + '@s.whatsapp.net'

def send_debug(message_content):
    methods_interface.call('message_send', (DEBUG_JID, str(message_content)))

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
    print 'Logging in'
    methods_interface.call('auth_login', (USERNAME, PASSWORD))

# Contacts

def cb_contact_gotProfilePicture(jid, picture_id, image_path):
    global phase, profile_picture_path
    print 'image_path', image_path
    profile_picture_path = image_path
    phase = True

# Send

def cb_message_delivered(jid, message_id):
    methods_interface.call('delivered_ack', (jid, message_id))

def cb_message_sent(jid, message_id):
    pass

# Main

def setup():
    Debugger.enabled = True    
    global cm, signals_interface, methods_interface
    print 'Settng up environment'


    cm = YowsupConnectionManager()

    cm.setAutoPong(True)

    signals_interface = cm.getSignalsInterface()
    methods_interface = cm.getMethodsInterface()

    signals_interface.registerListener('auth_success', cb_auth_success)
    signals_interface.registerListener('auth_fail', cb_auth_fail)
    signals_interface.registerListener('contact_gotProfilePicture', cb_contact_gotProfilePicture)
    signals_interface.registerListener('receipt_messageSent', cb_message_sent)
    signals_interface.registerListener('receipt_messageDelivered', cb_message_delivered)

    # Presence
    signals_interface.registerListener('presence_updated', cb_presence_updated)
    # signals_interface.registerListener('presence_available', cb_presence_updated)
    # signals_interface.registerListener('presence_unavailable', cb_presence_updated)
    
def cb_presence_updated(last_seen):
    """ callback for when presence is updated
    """
    print 'presence_updated', last_seen

def last_online(phone_number):
    """
    """
    global profile_picture_path, phase
    profile_picture_path = None
    jid = phone_number2jid(phone_number)
    phase = None
    print 'Calling presence_requests'
    # First set presence available for myself

    methods_interface.call('presence_sendAvailable')

    # methods_interface.call('presence_subscribe', (jid,))
    methods_interface.call('presence_request', (jid,))    

    print 'Called'
    while phase is None:
        time.sleep(0.5)
    
def generate_profile_picture(phone_number):
    global profile_picture_path, phase
    profile_picture_path = None
    jid = phone_number2jid(phone_number)
    phase = None
    print 'Calling contact_getProfilePicture'
    methods_interface.call('contact_getProfilePicture', (jid,))
    print 'Called'
    while phase is None:
        time.sleep(0.5)

def run():
    setup()
    login()
    while phase is None:
        time.sleep(0.5)

run()

#########
# Flask #
#########

# from flask import Flask, request, send_file

# app = Flask(__name__)

# @app.route('/whatspy/<phone_number>')
# def whatspy(phone_number):
#     global profile_picture_path
#     generate_profile_picture(phone_number)
#     # send_debug(request.remote_addr + ' :: ' + phone_number)
#     return send_file(profile_picture_path, mimetype='image/jpeg')

if __name__ == '__main__':
    maxnumber = '13104874553'
    # app.run(debug=True, port=5000)

    global profile_picture_path

    phone_number = maxnumber

    # send_debug('trying')
    # generate_profile_picture(phone_number)

    last_online(phone_number)
    # send_debug(request.remote_addr + ' :: ' + phone_number)
    # return send_file(profile_picture_path, mimetype='image/jpeg')
    
