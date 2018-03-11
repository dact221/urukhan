#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import cgi
import socketserver
import rauth
import threading
import requests

VERIFIER = None


def parse_address(address):
    """Create a tuple containing a string giving the address, and an
    integer port number.

    """
    base, port = address.split(':')
    return (base, int(port))


def create_callback_server(server_address):
    """Create the callback server that is used to set the oauth verifier
    after the request token is authorized.

    """
    class CallbackHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            global VERIFIER
            params = cgi.parse_qs(self.path.split('?', 1)[1],
                                  keep_blank_values=False)
            VERIFIER = params['oauth_verifier'][0]
            self.send_response(200)
            self.end_headers()
        def log_request(self, code='-', size='-'):
            pass
    return socketserver.TCPServer(server_address, CallbackHandler)


def get_khan_session(consumer_key, consumer_secret, username, password,
                     server_url='http://www.khanacademy.org',
                     callback_address='127.0.0.1:0'):

    """Create an authenticated Khan Academy API session using rauth
    OAuth 1.0 flow.

    This session give you access to the "Login Required" calls described
    in the API Explorer.

    You need a consumer key and consumer secret:

    http://www.khanacademy.org/api-apps/register

    You should also provide Khan Academy username and password.

    Only coachs can access information about other users.

    """

    # Create an OAuth1Service using rauth.
    service = rauth.OAuth1Service(
        consumer_key,
        consumer_secret,
        name = 'khan',
        request_token_url = server_url + '/api/auth2/request_token',
        access_token_url = server_url + '/api/auth2/access_token',
        authorize_url = server_url + '/api/auth2/authorize',
        base_url = server_url + '/api/auth2')

    callback_server = create_callback_server(parse_address(callback_address))

    # 1. Get a request token.
    request_token, secret_request_token = service.get_request_token(
        params={'oauth_callback': 'http://%s:%d/' %
            callback_server.server_address})

    # 2. Authorize your request token.
    params = {'oauth_token': request_token, 'identifier': username,
              'password': password}
    handle = threading.Thread(target=callback_server.handle_request)
    handle.start()
    requests.post(service.authorize_url, params)
    handle.join()
    callback_server.server_close()

    # 3. Get an access token.
    session = service.get_auth_session(request_token, secret_request_token,
                                       params={'oauth_verifier': VERIFIER})

    return session


class KhanSession:
    """Khan Academy API session.

    Loose wrapper class around Khan Academy rauth.OAuth1Session. If no
    user credentials given, it is a dummy class around request.Session.

    """
    def __init__(self, server_url='http://www.khanacademy.org',
                 consumer_key=None, consumer_secret=None,
                 username=None, password=None,
                 callback_address='127.0.0.1:0'):
        self.server_url = server_url
        if consumer_key and consumer_secret and username and password:
            self.session = get_khan_session(consumer_key, consumer_secret,
                                            username, password,
                                            server_url, callback_address)
        else:
            self.session = requests.Session()

    def call_api(self, rel_url, params={}):
        response = self.session.get(self.server_url + rel_url,
                                    params=params)
        return json.loads(response.text)
