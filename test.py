#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import khan_api
from secrets import *

def main(args):
    # To access public info:
    # k = khan_api.KhanSession()

    # To access user info:
    k = khan_api.KhanSession(
        server_url='http://www.khanacademy.org',
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        username=USERNAME,
        password=PASSWORD,
        callback_address='127.0.0.1:0')

    r = k.call_api('/api/v1/user')

    print(type(r))
    print(r)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
