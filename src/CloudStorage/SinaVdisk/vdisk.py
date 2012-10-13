#!/usr/bin/python
# -*- coding:utf-8 -*-

import argparse
import hmac
import hashlib
import time
import logging
import json

import requests

App_Key="2000904490"
App_Secret="0e4514df35df979dd1e58681319246e7"

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.DEBUG,datefmt='%m/%d %H:%M:%S')

## a wrapper function to request particular data to particular url
## logging the json info
## and return the reponse.json
def Vrequest(method,**kwargs):
    assert method in ['GET','POST'],"wrong method: %s"%method
    ## sometimes the api return nothing.
    while True:
        response=requests.request(method.lower(),**kwargs)
        if response.json is not None:
            returnedJson=response.json
            assert returnedJson.get("err_code") in [0,602],"fail.error code: %s,error message: %s" \
                   %(returnedJson["err_code"],returnedJson["err_msg"].encode('utf-8'))
            logging.info('success.')
            return returnedJson

class VdiskUser():
    
    def __init__(self,account,password,app_type=None):
        self.account=account
        self.password=password
        self.token=None
        self.app_type=app_type
        self.dologid=None
        self.used=None
        self.total=None

    def get_token(self):
        url="http://openapi.vdisk.me/?m=auth&a=get_token"
        t=int(time.time())
        if self.app_type is None:
            self.app_type="local"
        signature=hmac.new(App_Secret,"account="+self.account
                           +"&appkey="+App_Key+"&password="+
                           self.password+"&time="+
                           repr(t),hashlib.sha256).hexdigest()
        data=dict(account=self.account,
                  password=self.password,
                  appkey=App_Key,time=t,
                  signature=signature,
                  app_type=self.app_type)
        returnedJson=Vrequest("POST",**dict(url=url,data=data))
        self.token=returnedJson["data"]["token"]
        return returnedJson

    ## keep alive
    def keep(self):
        url="http://openapi.vdisk.me/?a=keep"
        data=dict(token=self.token,dilogid=self.dologid) if self.dologid!=None \
              else dict(token=self.token)
        time.sleep(0.5)
        returnedJson=Vrequest("POST",**dict(url=url,data=data))
        if returnedJson['err_code'] in [0,602]:
            self.dologid=returnedJson['dologid']
            
    def get_quota(self):
        url="http://openapi.vdisk.me/?m=file&a=get_quota"
        data=dict(token=self.token)
        returnedJson=Vrequest("POST",**dict(url=url,data=data))
        self.used=returnedJson['data']['used']
        self.total=returnedJson['data']['total']
        logging.warning('used: %s'%returnedJson['data']['used'])
        logging.warning('total: %s'%returnedJson['data']['total'])
        return returnedJson

# handle file and dir etc.
class VdiskFile(VdiskUser):
    
    ## upload and share,a file size must less than 10M
    ## there is another upload_file in vdisk api.but it donot share
    def upload_file(self,afile,dir_id=0,cover=None):
        url="http://openapi.vdisk.me/?m=file&a=upload_share_file"
        if cover is None:
            cover="yes"
        files={'file':afile}
        self.keep()
        data=dict(token=self.token,dir_id=dir_id,
                  cover=cover,dologid=self.dologid)
        returnedJson=Vrequest('POST',**dict(url=url,data=data,files=files))
        return returnedJson

    def delete_file(self,fid):
        url="http://openapi.vdisk.me/?m=file&a=delete_file"
        self.keep()
        data=dict(token=self.token,fid=fid,dologid=self.dologid)
        returnedJson=Vrequest("POST",**dict(url=url,data=data))
        return returnedJson

    def recycle_del_file(self,fid):
        url='http://openapi.vdisk.me/?m=recycle&a=delete_file'
        self.keep()
        data=dict(token=self.token,fid=fid,dologid=self.dologid)
        returnedJson=Vrequest("POST",**dict(url=url,data=data))
        return returnedJson
    
    def get_dir_list(self,dir_id=0):
        url="http://openapi.vdisk.me/?m=dir&a=getlist"
        data=dict(token=self.token,dir_id=dir_id)
        returnedJson=Vrequest("POST",**dict(url=url,data=data))
        return returnedJson
                    
    def get_file_info(self,fid):
        url="http://openapi.vdisk.me/?m=file&a=get_file_info"
        self.keep()
        data=dict(token=self.token,fid=fid,dologid=self.dologid)
        returnedJson=Vrequest("POST",**dict(url=url,data=data))
        return returnedJson
    
def main():
    parser=argparse.ArgumentParser(description="Sina Vdisk")
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--auth","-A",help='log in,enter account,\
    password and app_type,app_type is either local or sinat',nargs=3)
    group.add_argument("--upload","-U",help="Upload a file",nargs="?",
                       type=argparse.FileType("r"))
    group.add_argument("--delete","-D",help="Delete a file")
    group.add_argument("--query","-Q",help="Query file by key word")
    
    args=parser.parse_args()

    users=json.load(open('accounts.json','r'))['users']
    length=len(users)
    assert length>0

    if args.auth:
        newuser=dict(account=args.auth[0],password=args.auth[1],app_type=args.auth[2])
        users.append(newuser)
        json.dump({"users":users},open('accounts.json','w'))
        print "add user success. re-run to operate"
        return
    elif any([args.upload,args.delete,args.query]):
        account=users[length-1]['account']
        password=users[length-1]['password']
        app_type=users[length-1]['app_type']
        assert all([account,password]), \
               'please set correct account and password.'
        user=VdiskFile(account,password,app_type)
        user.get_token()
        user.get_quota()
        if args.upload:
            user.upload_file(args.upload)
            return
        elif args.delete or args.query:
            target=args.delete if args.delete else args.query
            localList=json.load(open('fileList.json','r'))
            if target in localList:
                fid=localList[target]
            else:
                fileList=user.get_dir_list()['data']['list']
                ##the name:id dict 
                name_list=dict([(i['name'],i['id']) for i in fileList])
                json.dump(name_list,open('fileList.json','w'))
                if target in name_list:
                    fid=name_list['target']
                else:
                    assert 0>1,"can't find such file : %s" \
                               %target.encode('utf-8')
            if args.delete:
                user.delete_file(fid)
                user.recycle_del_file(fid)
                logging.info('delete file success: %s'%args.delete)
                return
            elif args.query:
                url=user.get_file_info(fid)['data']['s3_url']
                logging.info("query success: %s"%args.query)
                print url
                return
    else:
        parser.print_help()
            
if __name__=='__main__':
    main()
