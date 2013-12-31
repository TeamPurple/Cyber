import re
import requests
import json
from util import cache
from config import FACEBOOK

@cache()
def lookup_facebook_by_phone(phone_number):
    """Given a phone number, return either a Facebook user ID or None"""

    # remove non-digits (such as hyphens) from the phone number
    normalized_phone = re.sub(r'\D', r'', str(phone_number))

    # these parameters are magic and I don't understand them, so I wouldn't be
    # surprised if something suddenly and unexpectedly breaks
    params = dict(
        value           = '["%s"]' % normalized_phone,
        context         = "facebar",
        grammar_version = FACEBOOK['grammar_version'],
        viewer          = FACEBOOK['user_id'],
        rsp             = "search",
        sid             = FACEBOOK['sid'],
        qid             = FACEBOOK['qid'],
        see_more        = "false",
        max_results     = "10",
        __user          = FACEBOOK['user_id'],
        __a             = "1",
        __dyn           = FACEBOOK['dyn'],
        __req           = FACEBOOK['req'],
        __rev           = FACEBOOK['rev'],

    )

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
        'cookie': FACEBOOK['cookie'],
    }
    r = requests.get("https://www.facebook.com/ajax/typeahead/search/facebar/query/", params=params, headers=headers)

    try:
        data = json.loads(r.text[9:])
        # return the uid of the first (and presumably only) match
        return data['payload']['entities'][0]['uid']
    except:
        # no matches
        return None
