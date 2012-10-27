#! /usr/bin/python
#coding:utf-8

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


class KuaiPanClient(object):
    def set_tokens(self, fin):
        dat = json.load(fin)
        for k in ('consumer_key', 'consumer_secret',
                  'oauth_token', 'oauth_token_secret'):
            if not dat.get(k):
                print >> sys.stderr, "Please run '--auth keys.txt' first"
                sys.exit(1)
        self.consumer = oauth2.Consumer(dat['consumer_key'],
                                        dat['consumer_secret'])
        self.token = oauth2.Token(dat['oauth_token'],
                                  dat['oauth_token_secret'])

    def sign_url(self, url):
        dat = urlparse(url)
        oauth_request = oauth2.Request.from_consumer_and_token(self.consumer,
                                           self.token, 'GET', url)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                                   self.consumer, self.token)
        return oauth_request, dat[1]

    def get(self, url):
        surl, host = self.sign_url(url)
        request = urllib2.Request(url)
        for header, value in surl.to_header().items():
            request.add_header(header, value)
        response = urllib2.urlopen(request)
        return response.read()

    def acquire_token(self, fout=sys.stdout):
        """Aquire an OAuth access token for the given user."""
        print "Please register to Kuaipan and get",
        print "consumer_key and consumer_secret, then input here:"
        consumer_key = raw_input("consumer_key:")
        consumer_secret = raw_input("consumer_secret:")
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)
        # Issue a new access token for the user.
        self.token = None
        url = "https://openapi.kuaipan.cn/open/requestToken"
        req, host = self.sign_url(url)
        res = urllib2.urlopen(req.to_url())
        dat = json.load(res)
        print "Please visit this url, then 'Enter'"
        print ("https://www.kuaipan.cn/api.php?ac=open&op=authorise"
               "&oauth_token=" + dat['oauth_token'])
        raw_input()
        # try to fetch access token
        self.token = oauth2.Token(dat['oauth_token'],
                                  dat['oauth_token_secret'])
        url = "https://openapi.kuaipan.cn/open/accessToken"
        req, host = self.sign_url(url)
        res = urllib2.urlopen(req.to_url())
        dat = json.load(res)
        self.token = oauth2.Token(dat['oauth_token'],
                                  dat['oauth_token_secret'])

        dat["consumer_key"] = consumer_key
        dat["consumer_secret"] = consumer_secret
        fout.write(json.dumps(dat))

    def query(self, word):
        req, host = self.sign_url("https://openapi.kuaipan.cn/1/"
                                  "metadata/app_folder/")
        res = urllib2.urlopen(req.to_url())
        data = json.load(res)
        print data
        for f in data['files']:
            if f.get('type') != 'file' or f.get('is_deleted'):
                continue
            fn = f.get('name')
            if not fn:
                continue
            fn = os.path.basename(fn)
            if word and word in fn:
                print fn

    def fetch(self, filename):
        # get download locate
        res = urllib2.urlopen("http://api-content.dfs.kuaipan.cn"
                              "/1/fileops/upload_locate")
        print res.read()
        return

        name = os.path.basename(filename)
        req, host = self.sign_url("https://api-content.dfs.kuaipan.cn"
                                  "/1/fileops/download_file")
        url = req.to_url() + "&" + urllib.urlencode({"root": "app_folder",
                                                     "path": name})
        print url
        res = urllib2.urlopen(url)
        print res.read()

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
    group.add_argument("--fetch", "-F", help="Download a file")

    args = parser.parse_args()
    clt = KuaiPanClient()

    if args.auth:
        # should save token into save place
        if args.auth == '-':
            clt.acquire_token()
        else:
            clt.acquire_token(open(args.auth, 'w'))
        sys.exit(0)

    if args.upload or args.delete or args.query or args.fetch:
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
    elif args.fetch:
        clt.fetch(args.fetch)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
