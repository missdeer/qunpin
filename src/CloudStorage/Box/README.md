Box:
===============================
URL: https://www.box.com/files
Usage:
box.py [option path]  
* option:
* --upload, -U filename  Upload local file to Box cloud storage service   
* --delete, -D filename  Delete the file in Box storage service  
* --query,  -Q keyword   Query the file by keyword in Box cloud storage service  
* --auth,   -A filename  get authorise from Box user, save keys in file  
* --fetch,  -F filename  get file from Box user

How to auth with box:
* Register App at http://box.com/developers/services/edit/
* run box.py --auth keys.txt
* Will be prompt to visit a url, copy/paste the url in browser, you will be ask to login  
  and allow APP
* go back and press 'Enter'
