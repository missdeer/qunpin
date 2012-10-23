Box:
===============================
Usage:
googledrive [option path]  
* option:
* --upload, -U filename  Upload local file to Google Drive cloud storage service   
* --delete, -D filename  Delete the file in Google Drive cloud storage service  
* --query,  -Q keyword   Query the file by keyword in Google Drive cloud storage service  
* -- auth,  -A filename  get authorise from GoogleDrive user, save keys in file  

How to auth with box:
* Register App at http://box.com/developers/services/edit/
* run box.py --auth keys.txt
* Will be prompt to visit a url, copy/paste the url in browser, you will be ask to login  
  and allow APP
* go back and press 'Enter'
