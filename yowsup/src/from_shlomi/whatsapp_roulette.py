import sys
import datetime

from whatsapp_client import WhatsappClient

wc = WhatsappClient()
incoming, outgoing = wc.get_queues()
wc.start()

while True:

    jid, timestamp, message_content = incoming.get()
    outgoing.put((jid, message_content))

    phone_number = jid.split('@')[0]
    formatted_date = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
    sys.stdout.write('%s %s : %s' % (formatted_date, phone_number, message_content) + '\r\n')
    sys.stdout.flush()