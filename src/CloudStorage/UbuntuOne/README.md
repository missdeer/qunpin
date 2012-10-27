UbuntuOne:
===============================
URL: https://one.ubuntu.com/dashboard/ , https://login.ubuntu.com/+applications
Usage:
ubuntuone.py [option path]
* option:
* --auth,   -A filename  get authorise from UbuntuOne user, save keys in file  
* --upload, -U filename  Upload local file to UbuntuOne cloud storage service  
* --delete, -D filename  Delete the file in UbuntuOne cloud storage service  
* --query,  -Q keyword   Query the file by keyword in UbuntuOne cloud storage service  
* --fetch,  -F filename  Download file from UbuntuOne cloud storage service  


Need use --auth to get authorise from user, save keys in file  
Then next time thise script can use this key/sec pair to access

Depenence:
* python 2.7
* oauth2  
    for red-hat linux:  
    yum install python-oauth2  
    
    or get from source:  
    https://github.com/simplegeo/python-oauth2
