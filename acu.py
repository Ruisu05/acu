import schedule
import time
from telethon import TelegramClient, events, sync
import json
from bs4 import BeautifulSoup
import requests
from mega import Mega
import os

with open('res.json') as json_file:
    data = json.load(json_file)
chan = str(data['ChannelU']) #Usuario del canal donde se envia los capitulos
api_id = int(data['api_id']) #api_id de cuenta de telegram que se usa para enviar  los capitulos
api_hash = str(data['api_hash']) #api_hash de cuenta de telegram que se usa para enviar  los capitulos
client = TelegramClient('session_name', api_id, api_hash)
client.start()
mu = str(data['mu']) #Usuario de Mega usado para descargar los capitulos
mp = str(data['mp']) #Contraseña de Mega usado para descargar los capitulos
pa = str(data['path']) #Path donde se guardan los archivos

def checkSend():
    l = 'https://tioanime.com'
    html_text = requests.get(l).text
    soup = BeautifulSoup(html_text, 'lxml')
    ta = soup.find_all('article', class_='episode')
    with open('chaps.json') as json_fil:
            ch = json.load(json_fil)
    for i in ta:
        nam = i.find('h3').string
        lnam = i.find('a').get('href')
        clnam = lnam[5:]
        thumbp = l + i.find('img').get('src')
        sthumb = i.find('img').get('src')[16:]
        if nam not in ch:
            url = l + i.find("a").get("href")
            img_data = requests.get(thumbp).content
            with open(sthumb, 'wb') as handler:
                handler.write(img_data)
            getMegaURL(url, clnam)
            path = pa + clnam + '.mp4'
            client.send_file(chan, path, support_streaming = True, caption = nam, thumb = sthumb)
            os.remove(clnam + ".mp4")
            os.remove(sthumb)
            print("Uploaded: " + nam)
            ch.update({nam: ""})
            with open('chaps.json', 'w') as f: #json donde guardo que capitulos se han subido
                json.dump(ch, f)

def getMegaURL(url, clnam):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    ful = soup.find("a", class_ = "btn-success")
    mega = Mega()
    m = mega.login(mu, mp)
    m.download_url(ful.get("href"), pa, clnam + ".mp4")
    

schedule.every(10).minutes.do(checkSend)

while True:
    schedule.run_pending()
    time.sleep(1)