#! /usr/bin/python

import os
import re
import sys
import json
import httplib
import argparse
from urlparse import urlparse
from mimetypes import guess_type
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
            print >> sys.stderr, "Has no auth_token,",
            print >> sys.stderr, "you should run --auth first"
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

    def auth_http(self, act, url, data="", hd={}):
        host = urlparse(url)[1]
        conn = httplib.HTTPSConnection(host)
        if 'authorization' not in hd:
            hd['authorization'] = ("BoxAuth api_key=%(api_key)s&"
                                   "auth_token=%(auth_token)s" % self.token)
        conn.request(act, url, data, hd)
        res = conn.getresponse()
        #print res.status
        #print res.reason
        #print res.getheaders()
        return res

    def _query(self, word, limit=100):
        # https://api.box.com/2.0/folders/FOLDER_ID/items
        # parameter: fileds, limit, offset
        # {"total_count":1,
        #  "entries":[{"type":"file",
        #              "id":"3663038953",
        #              "sequence_id":"1",
        #              "etag":"27d1999ed12adeb1739d47b1093019920aad7fd9",
        #              "name":"abcd.txt.webdoc"}]}
        url = "https://api.box.com/2.0/folders/0/items"
        ret = self.auth_http("GET", url).read()
        #print ret
        fs = []
        for entry in json.loads(ret)['entries']:
            if word in entry['name'] and entry["type"] == "file":
                fs.append(entry)
                #pprint(entry)
        return fs

    def query(self, word, limit=100):
        fs = self._query(word, limit)
        if fs:
            pprint(fs)

    def get_info(self, name):
        fs = self._query(name)
        for f in fs:
            if f['name'] == name:
                return f
        return None

    def fetch(self, filename):
        name = os.path.basename(filename)
        info = self.get_info(name)
        if not info:
            print >> sys.stderr, "Can not found file", name
            sys.exit(1)
        url = "https://api.box.com/2.0/files/" + info['id'] + "/content"
        res = self.auth_http("GET", url)
        url = res.getheader("location", "")
        if res.status == 302 and url:
            res = self.auth_http("GET", url)
        sys.stdout.write(res.read())

    def _delete(self, entry):
        url = "https://api.box.com/2.0/files/" + entry['id']
        hd = {"If-Match": entry['etag']}
        ret = self.auth_http("DELETE", url, "", hd).read()
        print ret.strip(),

    def delete(self, filename):
        # https://api.box.com/2.0/files/FILE_ID
        # query etag first
        name = os.path.basename(filename)
        entry = self.get_info(name)
        if not entry:
            print >> sys.stderr, "Not exists file", name
            sys.exit(1)
        self._delete(entry)

    def upload(self, filename):
        name = os.path.basename(filename)
        entry = self.get_info(name)
        if entry:
            self._delete(entry)
        #print "after check"
        size = os.path.getsize(filename)
        cype = guess_type(name)
        if not cype or not cype[0]:
            cype = "text/plain"
        else:
            cype = cype[0]

        url = "https://api.box.com/2.0/files/content"

        message = MIMEMultipart('mixed')
        # Message should not write out it's own headers.
        setattr(message, '_write_headers', lambda self: None)

        msg = MIMENonMultipart(*cype.split('/'))
        msg.add_header('Content-Disposition',
                       'form-data; name="f"; filename="%s"' % name)
        del msg["MIME-Version"]
        msg.set_payload(open(filename).read())
        message.attach(msg)

        msg = MIMENonMultipart("text", "plain")
        msg.add_header('Content-Disposition', 'form-data; name="folder_id"')
        del msg["Content-Type"]
        del msg["MIME-Version"]
        msg.set_payload('0')
        message.attach(msg)

        body = message.as_string()
        #print body
        #return
        bd = message.get_boundary()
        hd = {"Content-Type": "multipart/form-data; boundary=%s" % bd}
        res = self.auth_http("POST", url, body, hd)
        ret = res.read()

        print(json.loads(ret)["entries"][0]['name'])


def main():
    parser = argparse.ArgumentParser(description="Use command line to "
                                                 "control Box")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auth", "-A", help="Authorise by Box user")
    group.add_argument("--query", "-Q", help="Query file by key word")
    group.add_argument("--fetch", "-F", help="Download a file")
    group.add_argument("--upload", "-U", help="Upload a file")
    group.add_argument("--delete", "-D", help="Delete a file")

    args = parser.parse_args()
    clt = BoxClient()

    if args.auth:
        clt.acquire_token(KEYS_FILENAME)
        sys.exit(0)

    if args.upload or args.delete or args.query or args.fetch:
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
    elif args.fetch:
        clt.fetch(args.fetch)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
