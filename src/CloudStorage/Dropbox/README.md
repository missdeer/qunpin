Dropbox:
===============================
Usage:
dropbox [option path]
* option:
* --auth,   -A filename  get authorise from UbuntuOne user, save keys in file
* --upload, -U filename  Upload local file to Dropbox cloud storage service  
* --delete, -D filename  Delete the file in Dropbox cloud storage service  
* --query,  -Q keyword   Query the file by keyword in Dropbox cloud storage service  


Need use --auth to get authorise from dropbox user, save key and sec
Then next time this user can use this key/sec pair to access

Depenence:
    download dropbox sdk:
    https://www.dropbox.com/static/developers/dropbox-python-sdk-1.5.1.zip

    unzip and go into path:
    python setup.py install
