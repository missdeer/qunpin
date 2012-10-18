Google Drive:
===============================
Usage:
googledrive [option path]  
* option:
* --upload, -U filename  Upload local file to Google Drive cloud storage service   
* --delete, -D filename  Delete the file in Google Drive cloud storage service  
* --query,  -Q keyword   Query the file by keyword in Google Drive cloud storage service  
* -- auth,  -A filename  get authorise from GoogleDrive user, save keys in file  

How to auth with google drive:
* Register App at https://code.google.com/apis/console/
* create "Client ID for web applications"
* Add http://localhost:8080/oauth in Redirect URIs
* Download JSON, save file as keys.txt in GoogleDrive dir
* run googledrive.py --auth keys.txt
* Will be prompt to visit a url, copy/paste the url in browser, you will be ask to login  
  and allow APP, after that, you will see browser say can not acceess web page, beause  
  it can not redirect to http://localhost:8080/oauth , don't be panic, just see the url  
  and search the code=xxxxxxxxxxxxxxxxxxxxxxxxxxx, this is what you need
* copy/paste that xxxxxxxxxxxxxxxxxxx and press "Enter"

