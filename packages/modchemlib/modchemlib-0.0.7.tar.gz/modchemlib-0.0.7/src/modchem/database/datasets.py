import requests

def periodic_table():
   return requests.get("http://185.173.92.249:8100/periodic").json()
        
    