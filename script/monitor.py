import requests
from bs4 import BeautifulSoup
from contextlib import redirect_stdout
from urllib.parse import urlparse
from urllib.parse import urlencode
import json
import sqlite3
from sqlite3 import Error
import itertools
import datetime
import os
import re
import time
from colorama import Fore, Style
import traceback 
import sys 

print("#############################################################################################################")
print("#############################################################################################################")
print("#############################################################################################################")
print("###                                               LEAK MONITOR                                            ###")
print("#############################################################################################################")
print("#############################################################################################################")
###################Setup#####################
os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.getcwd()
#load settings
with open(path + '/config.json', 'r') as config_file:
    settings = json.load(config_file)

###################Database#####################
#Checks the database file in current directory
#creates the required structures or continues
conn = None
try:
    conn = sqlite3.connect('../db/osintDB.db')
    cn = conn.cursor()
    cn.execute('SELECT SQLITE_VERSION()')
    print('[+] --- SQLLite Version: ' + sqlite3.version)

    caz = conn.cursor()
#We check if the tables exists if not we create the database
    caz.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='tblData' ''')
#if the count is 1, then table exists
    if caz.fetchone()[0]==1:
        print()
    else :
        caz.execute('''CREATE TABLE IF NOT EXISTS tblData (Link text, DateDisc date, Source text, Current text)''')
        print('[+] --- Table created')
        #commit the changes to db			
    conn.commit()

except Error as e:
    print(e)
    exit()

###################GITHUB#####################
#Check if Github is enabled
#Parameters
keywords =  " " + settings['Github'][0]['gitwords'] + " " + settings['Github'][0]['domains']
first_session = requests.Session()
#print(keywords)
authvalue = settings['Github'][0]['gitauth']
authorization = f'token {authvalue}'
header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; P027 Build/MRA58L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.132 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'referer':'https://github.com',
        'Authorization': authorization,
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'}
pagenumber = (settings['Github'][0]['gitpages'])
links=[]

#Loop through file names and begin searching
print('[+] --- Now doing GitHub recon.')
try:
    for filename in settings['Github'][0]['gitfilenames']:
        for page in range(1, int(pagenumber)):
            URL = "https://api.github.com/search/code?page=" + str(page) + "&order=desc&q=filename%3A"+ filename + keywords + "&sort=indexed"
            request_result=requests.get(URL, headers=header)
            site_json = json.loads(request_result.text)
            time.sleep(4)
            if "items" in site_json:
                for item in site_json["items"]:
                    links.append(item.get('html_url'))

except Error as e:
    print("[!] -- ERROR GITHUB CONNECTION")

#Notify user we are done. Print out results 
print('[!] --- GitHub done.')
#print(*links,  sep = "\n")

#lets commit github data to database then clear our array
if links:
    cn.execute("UPDATE tblData SET Current = ? WHERE Source = ?", ('','Github'))
    conn.commit()
    now = datetime.datetime.now()
    for item in links:
        cn.execute("INSERT INTO tblData(Link,DateDisc,Source,Current) VALUES(?,?,?,?)", (item,now.strftime('%Y-%m-%d %H:%M:%S'),"Github", "X"))
        conn.commit()
    print('[!] --- GitHub data added to DB.')
else:
    print('[!] --- GitHub has no data.')

###################GOOGLE#####################
#Check if Google is enabled
#Parameters
keywords = ""
for keyword in settings['Google'][0]['domains']:
    keywords = keywords + "|" + keyword + "%20"

keywords = keywords.replace("|", "", 1)
cookvalue = settings['Google'][0]['googlekey']
header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; P027 Build/MRA58L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.132 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'referer':'https://google.com',
        #'cookie': cookvalue,
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'}
googleresults = (settings['Google'][0]['googleresults'])
pagenumber = (settings['Google'][0]['googlepages'])
links = []
pageslinks=[]
#Loop through file names and begin searching
print('[+] --- Now doing Google recon.')
try:
    for filename in settings['Google'][0]['sitesinurl']:
        for page in range(0, int(pagenumber)):
            URL = "https://google.com/search?q=intext:" + keywords + "&as_sitesearch=" + filename + "&num="+googleresults+""
            #print(URL)
            request_result=requests.get(URL, headers=header)
            #print(request_result.status_code)
            time.sleep(2)
            if request_result.status_code == 200:
                soup = BeautifulSoup(request_result.content,'html.parser')
                div = soup.find('div', {'class':'nagivation'})
                for item in ([a['href'] for a in soup.find_all("a",{"class":"C8nzq BmP5tf"}, href=True)]):
                    links.append(item)

except Error as e:
    print("[!] -- ERROR GOOGLE CONNECTION")

#Notify user we are done. Print out results
print('[!] --- Google done.')
#print(*links,  sep = "\n")

# lets commit google data to database then clear our array
if links:
    cn.execute("UPDATE tblData SET Current = ? WHERE Source = ?", ('', 'Google'))
    conn.commit()
    now = datetime.datetime.now()
    for item in links:
        cn.execute("INSERT INTO tblData(Link,DateDisc,Source,Current) VALUES(?,?,?,?)",
                    (item, now.strftime('%Y-%m-%d %H:%M:%S'), "Google", "X"))
        conn.commit()
print('[!] --- Google data added to DB.')

###################FILTERING NEW ONLY#####################
try:
    print('\n------NEW RECORDS ------\n')
    cn.execute("SELECT * FROM (SELECT Link FROM tblData GROUP BY Link HAVING COUNT(Link) = ? AND Current = ?) AS ONLY_ONCE", (1,'X'))
    myresult = cn.fetchall()
    for x in myresult:
        print(x)
    
except Error as e:
   traceback.print_exception(*sys.exc_info()) 

#Notify user we are done. Print out results 
print('[!] --- Script Done ---')

