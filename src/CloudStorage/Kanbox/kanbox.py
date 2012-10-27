#! /usr/bin/python

import os
import sys
import json
import httplib
import argparse
from hashlib import md5
from pprint import pprint
from urllib import urlencode
from urlparse import urlparse
from mimetypes import guess_type
from datetime import datetime, timedelta


KEYS_FILENAME = 'keys.txt'


class KanBoxClient(object):     # most like google driver
    def http(self, act, url, data="", hd={}):
        ret = urlparse(url)
        h, host = ret[0] + '://' + ret[1], ret[1]
        path = url[len(h):]
        conn = httplib.HTTPSConnection(host)
        conn.request(act, url, data, hd)
        res = conn.getresponse()
        ret = res.read()
        #print ret
        #print res.status
        #print res.reason
        #print res.getheaders()
        return ret

    def auth_http(self, act, url, data="", hd={}):
        ret = urlparse(url)
        h, host = ret[0] + '://' + ret[1], ret[1]
        path = url[len(h):]
        conn = httplib.HTTPSConnection(host)
        if 'Authorization' not in hd:
            a = "Bearer " + self.token['access_token']
            hd['Authorization'] = a
        if 'Host' not in hd:
            hd['Host'] = host
        conn.request(act, path, data, hd)
        res = conn.getresponse()
        #print res.status
        #print res.reason
        #print res.getheaders()
        return res

    def check_auth(self, infn):
        if not os.path.isfile(infn):
            print >> sys.stderr, "Can not find", infn, "you have goto"
            print >> sys.stderr, "http://open.kanbox.com/ register"
            print >> sys.stderr, "Please check README.md for detail"
            sys.exit(1)
        try:
            self.token = t = json.load(open(infn))
        except Exception, e:
            print >> sys.stderr, e
            t = {}
        if 'access_token' not in t or 'refresh_token' not in t:
            print >> sys.stderr, "you have run '--auth %s'" % infn
            print >> sys.stderr, "to get auth before any operation"
            sys.exit(1)
        edt = datetime.strptime(self.token.get('before_this_time',
                                               "2000-01-01 00:00:00"),
                                "%Y-%m-%d %H:%M:%S")
        if edt < datetime.today():
            self.refresh_token()
            json.dump(self.token, open(infn, 'w'))

    def _update_token(self, ret):
        dat = json.loads(ret)
        for k, v in dat.items():
            self.token[k] = v
        sec = self.token['expires_in'] / 2
        edt = datetime.today() + timedelta(seconds=sec)
        self.token['before_this_time'] = edt.strftime("%F %T")

    def refresh_token(self):
        url = "https://auth.kanbox.com/0/token"
        data = urlencode({"refresh_token": self.token['refresh_token'],
                          "client_id": self.token['client_id'],
                          "client_secret": self.token['client_secret'],
                          "grant_type": "refresh_token",
                         })
        ret = self.http("POST", url, data,
                        {"Content-Type": "application/x-www-form-urlencoded"})
        self._update_token(ret)

    def acquire_token(self, infn):
        self.token = json.load(open(infn))
        pa = {
            "response_type": "code",
            "client_id": self.token['client_id'],
            "redirect_uri": "http://localhost:8080/oauth",
            }
        print "Visit this url, input the code:"
        print "https://auth.kanbox.com/0/auth?" + urlencode(pa)
        code = raw_input("code:")
        url = "https://auth.kanbox.com/0/token"
        data = urlencode({"code": code,
                          "client_id": self.token['client_id'],
                          "client_secret": self.token['client_secret'],
                          "redirect_uri": "http://localhost:8080/oauth",
                          "grant_type": "authorization_code",
                         })
        ret = self.http("POST", url, data,
                        {"Content-Type": "application/x-www-form-urlencoded"})
        self._update_token(ret)
        json.dump(self.token, open(infn, 'w'))

    def download(self, filename):
        url = "https://api.kanbox.com/0/download/" + filename.lstrip('/')
        res = self.auth_http("GET", url)
        """
        [('x-powered-by', 'PHP/5.2.17'),
         ('transfer-encoding', 'chunked'),
         ('server', 'nginx/1.0.5'),
         ('connection', 'keep-alive'),
         ('location', 'https://teldl-nj.kanbox.com/gcid2?'
                      'gcid=B22892B0E0B47D70A6CFEE297B886C2AAD10132A&'
                      'fn=README.md&userid=68980128&'
                      'sessionid=2d42a6e4440b492286d270b167eb13cb'),
         ('date', 'Thu, 25 Oct 2012 00:48:03 GMT'),
         ('content-type', 'text/html')]
        """
        if res.status == 302:
            res = self.auth_http("GET", res.getheader('location'))
        print res.read()

    def query(self, word, limit=100):
        url = "https://api.kanbox.com/0/list"
        res = self.auth_http("GET", url)
        dat = res.read()
        files = json.loads(dat)['contents']
        for info in files:
            name = os.path.basename(info['fullPath'])
            if word in name and not info['isFolder']:
                pprint(info)

    def delete(self, filename):
        name = os.path.basename(filename)
        # GET http://api.kabnbox.com/delete/pictures/flower.jpg
        url = "https://api.kanbox.com/0/delete/" + name
        ret = self.auth_http("GET", url).read()
        pprint(ret)

    def upload1(self, filename):
        name = os.path.basename(filename)
        # kanbox do support this way, which I don't like
        url = "https://api-upload.kanbox.com/0/upload/" + name
        body = open(filename).read()
        res = self.auth_http("POST", url, body)
        ret = res.read()
        pprint(ret)

    def upload(self, filename):
        name = os.path.basename(filename)
        size = os.path.getsize(filename)
        cype = guess_type(name)
        if not cype or not cype[0]:
            cype = "text/plain"
        else:
            cype = cype[0]

        url = "https://api-upload.kanbox.com/0/upload/" + name
        # kanbox not work with MIME lib, it request '\r\n', but lib only '\n'
        # so we manually construct it here
        bd = "-----" + md5(filename).hexdigest()
        body = "\r\n".join(("--" + bd,
                'Content-Disposition: '
                'form-data; name="f"; filename="%s"' % name,
                "Content-Type: %s" % cype,
                "",
                open(filename).read(),
                "",
                "--%s--" % bd,
                ))
        hd = {"Content-Type": "multipart/form-data; boundary=%s" % bd}
        res = self.auth_http("POST", url, body, hd)
        ret = res.read()
        #pprint(ret)


def main():
    parser = argparse.ArgumentParser(description="Use command line to "
                                                 "control GoogleDrive")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auth", "-A", help="Authorise by google drive user")
    group.add_argument("--query", "-Q", help="Query file by key word")
    group.add_argument("--fetch", "-F", help="Fetch a file")
    group.add_argument("--upload", "-U", help="Upload a file")
    group.add_argument("--delete", "-D", help="Delete a file")

    args = parser.parse_args()
    clt = KanBoxClient()

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
        clt.download(args.fetch)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
