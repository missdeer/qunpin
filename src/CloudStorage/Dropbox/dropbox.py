#! /usr/bin/python

import os
import sys
import argparse

# Include the Dropbox SDK libraries
from dropbox import client, rest, session


# Get your app key and secret from the Dropbox developer website
APP_KEY = 'egsenb3c6k0t1bh'
APP_SECRET = 'rhhj1hwjzb0v4ha'
# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'


class DropBoxClient(object):
    def __init__(self, key, sec):
        # key and sec are got from auth
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        sess.set_token(key, sec)
        self.client = client.DropboxClient(sess)
        #print "linked account:", client.account_info()

    def auth(self):
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        request_token = sess.obtain_request_token()
        url = sess.build_authorize_url(request_token)
        # Make the user sign in and authorize this token
        print "url:", url
        print "Please visit this website and press the",
        print "'Allow' button, then hit 'Enter' here."
        raw_input()
        try:
            # will fail if the user didn't visit the above URL and hit 'Allow'
            access_token = sess.obtain_access_token(request_token)
            print "please save these for the account"
            print "key:", repr(access_token.key)
            print "sec:", repr(access_token.secret)

            client = client.DropboxClient(sess)
            print "linked account:", client.account_info()
        except Exception:
            print >> sys.stderr, "Failed to get access token"

    def meta(self, filename):
        f, metadata = self.client.get_file_and_metadata('/magnum-opus.txt')
        out = open('magnum-opus.txt', 'w')
        out.write(f.read())
        print(metadata)

    def _remote_path(self, local_filename):
        name = os.path.basename(local_filename)
        return os.path.join("/", name)

    def upload(self, filename):
        fobj = open(filename)
        ret = self.client.put_file(self._remote_path(filename), fobj,
                                   overwrite=False, parent_rev=None)
        print ret

    def delete(self, filename):
        self.client.file_delete(self._remote_path(filename))

    def query(self, word):
        ret = self.client.search('/', word, file_limit=1000,
                                 include_deleted=False)
        print ret


def main():
    parser = argparse.ArgumentParser(description="Use command line to "
                                                 "control dropbox")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auth", "-A", help="Authorise by dropbox user")
    group.add_argument("--upload", "-U", help="Upload a file")
    group.add_argument("--delete", "-D", help="Delete a file")
    group.add_argument("--query", "-Q", help="Query file by key word")

    args = parser.parse_args()

    if args.upload or args.delete or args.query or args.auth:
        clt = DropBoxClient('5k9obasoquq0qhv', '3av8u8gcvepe547')
    else:
        parser.print_help()
        sys.exit(1)

    if args.upload:
        clt.upload(args.upload)
    elif args.delete:
        clt.delete(args.delete)
    elif args.query:
        clt.query(args.query)
    elif args.auth:
        clt.query(args.auth)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
