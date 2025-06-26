import schedule
import time
from telethon import TelegramClient, events, sync
import json
from bs4 import BeautifulSoup
import requests
import os
import subprocess
from pathlib import Path
import threading

# Configuration setup
CONFIG_FILE = 'res.json'
CHAPS_FILE = 'chaps.json'
BASE_URL = 'https://tioanime.com'
REQUEST_TIMEOUT = 10
LOCK = threading.Lock()

# Load configuration
try:
    with open(CONFIG_FILE) as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: {CONFIG_FILE} not found.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in {CONFIG_FILE}: {e}")
    exit(1)
    
chan = str(data['ChannelU']) #Usuario del canal donde se envia los capitulos
api_id = int(data['api_id']) #api_id de cuenta de telegram que se usa para enviar  los capitulos
api_hash = str(data['api_hash']) #api_hash de cuenta de telegram que se usa para enviar  los capitulos
client = TelegramClient('session_name', api_id, api_hash)
client.start()
pa = str(data['Path']) #Path donde se guardan los archivos

def checkSend():
    l = 'https://tioanime.com'
    # Intenta enviar una solicitud GET al sitio web y obtener el contenido HTML
    try:
        html_text = requests.get(l).text
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to access the website. {e}")
        return
    # Intenta crear una instancia de BeautifulSoup con el contenido HTML
    try:
        soup = BeautifulSoup(html_text, 'lxml')
    except TypeError as e:
        print(f"Error: Failed to parse the HTML content. {e}")
        return
    ta = soup.find_all('article', class_='episode')
    # Intenta abrir el archivo JSON con los episodios que se han enviado al canal de Telegram
    try:
        with open('chaps.json') as json_fil:
            ch = json.load(json_fil)
    except FileNotFoundError:
        print("Error: chaps.json file not found.")
        return
    except json.decoder.JSONDecodeError:
        print("Error: Invalid JSON in chaps.json file.")
        return
    for i in ta:
        nam = i.find('h3').text
        if "[email" in nam:
            continue
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
            path = pa + clnam + '.MP4'
            try:
                client.send_file(chan, path, supports_streaming = True, caption = nam, thumb = sthumb)
                os.remove(clnam + ".MP4")
            except Exception as e:
                print("Fallo al intentar subir el capitulo. Probable link caido.")
            os.remove(sthumb)
            print("Uploaded: " + nam)
            ch.update({nam: ""})
            with open('chaps.json', 'w') as f: #json donde guardo que capitulos se han subido
                json.dump(ch, f)

def getMegaURL(url, clnam):
    try:
        html_text = requests.get(url).text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
        return
    soup = BeautifulSoup(html_text, 'lxml')
    ful = soup.find("a", class_ = "btn-success")
    mlink = ful.get("href")
    try:
        subprocess.run(f"mega-get {mlink} /home/ubuntu/acu/{clnam}.MP4", shell=True)
    except Exception as e:
        if "Account blocked" in str(e):
            print("Link Caido")
    

schedule.every(10).seconds.do(checkSend)

while True:
    schedule.run_pending()
    time.sleep(1)