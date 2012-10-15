UbuntuOne:
===============================
Usage:
dropbox [option path]
* option:
* --auth,   -A filename  get authorise from UbuntuOne user, save keys in file  
* --upload, -U filename  Upload local file to Dropbox cloud storage service  
* --delete, -D filename  Delete the file in Dropbox cloud storage service  
* --query,  -Q keyword   Query the file by keyword in Dropbox cloud storage service  


Need use --auth to get authorise from user, save keys in file  
Then next time thise script can use this key/sec pair to access

Depenence:
* python 2.7
* oauth2  
    for red-hat linux:  
    yum install python-oauth2  
    
    or get from source:  
    https://github.com/simplegeo/python-oauth2
