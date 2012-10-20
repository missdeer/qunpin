#! /usr/bin/python

import os
import sys
import json
import base64
import urllib
import urllib2
import httplib
import argparse
from getpass import getpass
from mimetypes import guess_type
from urlparse import urlparse, parse_qs

import oauth2


KEYS_FILENAME = 'keys.txt'


class Unauthorized(Exception):
    """The provided email address and password were incorrect."""


class UbuntuOneClient(object):
    def set_tokens(self, fin):
        dat = parse_qs(fin.readline().strip())
        self.consumer = oauth2.Consumer(dat['oauth_consumer_key'][0],
                                        dat['oauth_consumer_secret'][0])
        dat = parse_qs(fin.readline().strip())
        self.token = oauth2.Token(dat['oauth_token'][0],
                                  dat['oauth_token_secret'][0])

    def sign_url(self, url):
        dat = urlparse(url)
        oauth_request = oauth2.Request.from_consumer_and_token(self.consumer,
                                           self.token, 'GET', url)
        oauth_request.sign_request(oauth2.SignatureMethod_PLAINTEXT(),
                                   self.consumer, self.token)
        return oauth_request, dat[1]

    def get(self, url):
        surl, host = self.sign_url(url)
        request = urllib2.Request(url)
        for header, value in surl.to_header().items():
            request.add_header(header, value)
        response = urllib2.urlopen(request)
        return response.read()

    def acquire_token(self, email_address, password, fout=sys.stdout):
        """Aquire an OAuth access token for the given user."""
        # Issue a new access token for the user.
        request = urllib2.Request(
            'https://login.ubuntu.com/api/1.0/authentications?' +
            urllib.urlencode({'ws.op': 'authenticate',
                              'token_name': 'Ubuntu One @ ubuntu [qunpin]'}))
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic %s' % base64.b64encode(
                           '%s:%s' % (email_address, password)))
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError, exc:
            if exc.code == 401:     # Unauthorized
                raise Unauthorized("Bad email address or password")
            else:
                raise
        data = json.load(response)
        self.consumer = oauth2.Consumer(data['consumer_key'],
                                        data['consumer_secret'])
        self.token = oauth2.Token(data['token'], data['token_secret'])

        # Tell Ubuntu One about the new token.
        self.get('https://one.ubuntu.com/oauth/sso-finished-so-get-tokens/')
        fout.write(str(self.consumer))
        fout.write("\n")
        fout.write(self.token.to_string())
        fout.write("\n")

    def query(self, word):
        res = self.get("https://one.ubuntu.com/api/file_storage/"
                       "v1/~/Ubuntu%20One?include_children=true")
        data = json.loads(res)
        #print data['children'][0]['content_path']
        for child in data['children']:
            if child.get('kind') != 'file':
                continue
            fn = child.get('content_path')
            if not fn:
                continue
            fn = os.path.basename(fn)
            if word and word in fn:
                print fn

    def put(self, act, url, mime="", data=""):
        sreq, host = self.sign_url(url)
        conn = httplib.HTTPSConnection(host)
        hd = dict(sreq.to_header().items())
        if mime:
            hd["Content-Type"] = mime
        #print hd
        conn.request(act, url, data, hd)
        res = conn.getresponse()
        ret = res.read()
        #print ret
        #print res.status
        #print res.reason
        #print res.getheaders()

    def delete(self, filename):
        name = os.path.basename(filename)
        url = ("https://one.ubuntu.com/api/file_storage/v1"
               "/~/Ubuntu%20One/" + urllib.quote(name))
        self.put("DELETE", url)

    def upload(self, filename):
        name = os.path.basename(filename)
        url = ("https://files.one.ubuntu.com/content"
               "/~/Ubuntu%20One/" + urllib.quote(name))
        mime = guess_type(name)
        if not mime or not mime[0]:
            mime = "text/plain"
        else:
            mime = mime[0]
        self.put("PUT", url, mime, open(filename))


def main():
    parser = argparse.ArgumentParser(description="Use command line to "
                                                 "control UbuntuOne")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auth", "-A", help="Authorise by ubuntuone user")
    group.add_argument("--query", "-Q", help="Query file by key word")
    group.add_argument("--upload", "-U", help="Upload a file")
    group.add_argument("--delete", "-D", help="Delete a file")

    args = parser.parse_args()
    clt = UbuntuOneClient()

    if not os.path.isfile(KEYS_FILENAME):
        print >> sys.stderr, "Can not find", KEYS_FILENAME
        print >> sys.stderr, "you have run '--auth ", KEYS_FILENAME
        print >> sys.stderr, "'generate first"
        sys.exit(1)

    if args.auth:
        print "Please submit  email address and password",
        print "to verify UbuntiOne account"
        email = raw_input("email:")
        passd = getpass()
        # should save token into save place
        if args.auth == '-':
            clt.acquire_token(email, passd)
        else:
            clt.acquire_token(email, passd, open(args.auth, 'w'))
        sys.exit(0)

    if args.upload or args.delete or args.query:
        # should get token from some secure place
        # here just hard code for testing
        clt.set_tokens(open(KEYS_FILENAME))
    else:
        parser.print_help()
        sys.exit(1)

    if args.upload:
        clt.upload(args.upload)
    elif args.delete:
        clt.delete(args.delete)
    elif args.query:
        clt.query(args.query)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
