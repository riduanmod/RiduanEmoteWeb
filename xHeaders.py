import os, json, time, urllib3, random, ssl, aiohttp
import requests
from threading import Thread

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

# টোকেন জেনারেটর/ক্যাশ
def ToK():
    while True:
        try:
            r = requests.get('https://tokens-asfufvfshnfkhvbb.francecentral-01.azurewebsites.net/ReQuesT?&type=ToKens')
            t = r.text
            i = t.find("ToKens : [")
            if i != -1:
                j = t.find("]", i)
                L = [x.strip(" '\"") for x in t[i+11:j].split(',') if x.strip()]
                if L:
                    with open("token.txt", "w") as f:
                        f.write(random.choice(L))
        except: pass
        time.sleep(5 * 60 * 60)

Thread(target=ToK, daemon=True).start()

def GeTToK():
    try:
        with open("token.txt") as f: return f.read().strip()
    except: return "No_Token_Found"
