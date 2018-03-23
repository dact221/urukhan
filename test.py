#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# test.py host port rcon_password
#
# Example:
# test.py 0.0.0.0 25575 rc0n_p4ssw0rd
#

import khan_api
import mcrcon
from secrets import *

def main(host, port, password):

    k = khan_api.KhanSession(
        server_url='https://www.khanacademy.org',
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        username=USERNAME,
        password=PASSWORD,
        callback_address='127.0.0.2:0')

    rcon = mcrcon.MCRcon()
    rcon.connect(host, port, password)

    mc_username = input('Minecraft username: ')
    khan_email = input('Khan Academy email: ')

    points = k.get_user(email=khan_email)['points']
    print('\nUser %s has %d points.' % (khan_email, points))

    REWARD = input("\nReward item name (e. g. minecraft:diamond): ")

    print('\nExchange:\nX points = 1 reward item.')
    exchange_rate = int(input('\nX = '))

    n = points // exchange_rate
    response = rcon.command('give %s %s %d' % (mc_username, REWARD, n))
    if response:
        print("  %s" % response)

    rcon.disconnect()
    return 0

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) != 3:
        print("usage: python demo.py <host> <port> <password>")
        sys.exit(1)
    host, port, password = args
    port = int(port)
    sys.exit(main(host, port, password))
