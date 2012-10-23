#! /usr/bin/python

import os
import re
import sys
import json
import base64
import urllib2
import httplib
import argparse
from hashlib import md5
from getpass import getpass
from urllib import urlencode
from mimetypes import guess_type
from urlparse import urlparse, parse_qs
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from pprint import pprint


KEYS_FILENAME = 'keys.txt'


class BoxClient(object):
    def http(self, act, url, data="", hd={}):
        host = urlparse(url)[1]
        conn = httplib.HTTPSConnection(host)
        conn.request(act, url, data, hd)
        res = conn.getresponse()
        ret = res.read()
        #print ret
        #print res.status
        #print res.reason
        #print res.getheaders()
        return ret

    def check_auth(self, infn):
        self.token = json.load(open(infn))
        if not self.token.get("auth_token"):
            print >> sys.stderr, "Has no auth_token, you should run --auth first"
            sys.exit(1)

    def acquire_token(self, infn):
        re1 = re.compile("\<ticket\>([^<>]+)\</ticket\>")
        re2 = re.compile("\<auth_token\>([^<>]+)\</auth_token\>")
        self.token = json.load(open(infn))
        appkey = self.token.get("api_key")
        if not appkey:
            print >> sys.stderr, "You should get an API Key first from"
            print >> sys.stderr, "http://box.com/developers/services/edit/"
            sys.exit(1)

        url = ("https://www.box.com/api/1.0/rest?"
               "action=get_ticket&api_key=" + api_key)
        ret = self.http("GET", url)
        ticket = re1.search(data).groups()[0].strip()
        print "https://www.box.com/api/1.0/auth/" + ticket
        raw_input("Please visit this url, then press [Enter]:")

        url = ("https://www.box.com/api/1.0/rest?action=get_auth_token"
               "&api_key=%s&ticket=%s" % (api_key, ticket))
        ret = self.http("GET", url)
        auth = re2.search(data).groups()[0].strip()

        self.token['auth_token'] = auth
        json.dump(self.token, open(infn, 'w'))

    def query(self, word, limit=100):
        # can not use contain, it is a bug:
        # http://stackoverflow.com/questions/12695434/
        # google-drive-title-contains-query-not-working-as-expected
        q = urlencode({#"q": "title contains 'bcd'",
                       "maxResults": limit})
        files = self._query(q)
        for info in files:
            if word in info['title'] and info["kind"] == "drive#file":
                pprint({"title": info['title'], "file_id": info['id']})

    def auth_http(self, act, url, data="", hd={}):
        host = urlparse(url)[1]
        conn = httplib.HTTPSConnection(host)
        if 'authorization' not in hd:
            a = self.token['token_type'] + " " + self.token['access_token']
            hd['authorization'] = a
        conn.request(act, url, data, hd)
        res = conn.getresponse()
        return res

    def delete(self, filename):
        name = os.path.basename(filename)
        q = urlencode({"q": "title = '%s'" % name.replace("'", r"\'"),
                       "maxResults": 2})
        try:
            files = self._query(q)
            fid = files[0]['id']
        except (KeyError, IndexError), e:
            print >> sys.stderr, name, "not found"
            sys.exit(1)
        url = "https://www.googleapis.com/drive/v2/files/" + fid
        #a = self.token['token_type'] + " " + self.token['access_token']
        #ret = self.http("DELETE", url, "", {"authorization": a})
        ret = self.auth_http("DELETE", url).read()
        pprint(ret)

    def upload(self, filename):
        name = os.path.basename(filename)
        size = os.path.getsize(filename)
        cype = guess_type(name)
        if not cype or not cype[0]:
            cype = "text/plain"
        else:
            cype = cype[0]

        url = ("https://www.googleapis.com/upload/drive/v2/files?"
               "uploadType=multipart")

        message = MIMEMultipart('mixed')
        # Message should not write out it's own headers.
        setattr(message, '_write_headers', lambda self: None)

        msg = MIMENonMultipart('application', 'json; charset=UTF-8')
        msg.set_payload(json.dumps({"title": name,  #.replace("'", r"\'"),
                                    "mimeType": cype}))
        message.attach(msg)

        msg = MIMENonMultipart(*cype.split('/'))
        msg.add_header("Content-Transfer-Encoding", "binary")
        msg.set_payload(open(filename).read())
        message.attach(msg)
        
        body = message.as_string()
        bd = message.get_boundary()
        hd = {"Content-Type": 'multipart/related; boundary="%s"' % bd}
        res = self.auth_http("POST", url, body, hd)
        ret = res.read()
        pprint(ret)
        return 


def main():
    parser = argparse.ArgumentParser(description="Use command line to "
                                                 "control GoogleDrive")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auth", "-A", help="Authorise by google drive user")
    group.add_argument("--query", "-Q", help="Query file by key word")
    group.add_argument("--upload", "-U", help="Upload a file")
    group.add_argument("--delete", "-D", help="Delete a file")

    args = parser.parse_args()
    clt = BoxClient()

    if args.auth:
        clt.acquire_token(KEYS_FILENAME)
        sys.exit(0)

    if args.upload or args.delete or args.query:
        clt.check_auth(KEYS_FILENAME)
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
