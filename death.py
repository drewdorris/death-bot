import requests
import time
import os
import urllib.request
import urllib.error
import glob
import tweepy
from PIL import Image
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime

olddeadpeople = []
consumer_key = "xxx"
consumer_secret = "xxx"
access_token = "xxx"
access_token_secret = "xxx"

# adding path to geckodriver to the OS environment variable
# assuming that it is stored at the same path as this script
# this is for the image searching stuff
os.environ["PATH"] += os.pathsep + os.getcwd()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

client = tweepy.Client(consumer_key=consumer_key, consumer_secret=consumer_secret,
                       access_token=access_token, access_token_secret=access_token_secret)

api = tweepy.API(auth)
#api.update_status("asdf")

# this method is kind of unnecessary but it cleans up things a bit
# just prints the death message and calls the image searcher
def handle_death(death):
    print(datetime.now(), death)

    img_url = get_image(death)
    print(img_url)

    media1 = api.simple_upload(img_url)
    media2 = api.simple_upload("rob.jpg")
    #api.update_status(status=death + " just passed away, and I just passed gas! #fart", media_ids=[media1.media_id, media2.media_id])
    response = client.create_tweet(text=death + " just passed away, and I just passed gas! #fart", media_ids=[media1.media_id, media2.media_id])

def get_image(death):
    url = "https://www.google.com/search?q="+death+"&source=lnms&tbm=isch"
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)
    driver.get(url)

    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    extensions = {"jpg", "jpeg", "png", "gif"}

    # imges = driver.find_elements_by_xpath('//div[@class="rg_meta"]') # not working anymore
    # imges = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    imgs = driver.find_elements_by_css_selector("img.Q4LuWd")
    print ("Total images:", len(imgs), "\n")
    print ("Downloading...")
    for img in imgs:
        img_url = img.get_attribute('src')
        #print ("Downloading image", img_count, ": ", img_url)
        try:
            urllib.request.urlretrieve(img_url, "dataset/"+death.replace(" ", "_")+".jpg")            #req = urllib.request.Request(img_url, headers=headers)
            #raw_img = urllib.request.urlopen(req).read()
            #f = open("dataset/"+death.replace(" ", "_")+"."+img_type, "wb")
            #f.write(raw_img)
            #f.close
        except Exception as e:
            print("Download failed:", e) # Download failed: [Errno 2] No such file or directory: 'dataset/Big_Pokey.jpg'
        finally:
            #print
            break
    driver.quit()
    resize_images(death)
    return "dataset/"+death.replace(" ", "_")+".jpg"

def resize_images(name):
    print("Converting image...")
    time.sleep(2)
    for file in glob.glob("dataset\\" + name.replace(" ", "_") + "\\*.jpg"):
        i = Image.open(file);
        i = i.resize((500, 400))
        i = i.convert('RGB')
        i.save(file)

while True:
    query = '''PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?item ?itemLabel ?article
    {
            ?item wdt:P570 ?dod
            FILTER ( ?dod > "2020-12-08T00:00:00Z"^^xsd:dateTime)
            FILTER ( ?dod > (now()-"P32D"^^xsd:duration) && ?dod < now() )
            ?item wdt:P31 wd:Q5 .
        ?article schema:about ?item .
        ?article schema:inLanguage "en" .
        FILTER (SUBSTR(str(?article), 1, 25) = "https://en.wikipedia.org/")
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    ORDER BY DESC(?dod) ?item
    LIMIT 200
    '''

    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    dataRaw = requests.get(url, params={'query': query, 'format': 'json'}, headers={'User-Agent': 'DeathBot/0.0 (https://github.com/drewdorris; contact@dorrisd.com)'})
    if not dataRaw:
        print('Data not found!')
        time.sleep(60 * 5)
        continue
    
    data = dataRaw.json()
    deadpeople = []
    for item in data['results']['bindings']:
        deadpeople.append(item['itemLabel']['value'])

    for idx, x in enumerate(deadpeople):
        if not olddeadpeople:
            break
        if x not in olddeadpeople:
            if len(x) > 2 and x[0] == 'Q' and x[1].isdigit():
                print('??? ', x)
                continue
            handle_death(x)
    
    olddeadpeople = deadpeople
    time.sleep(60 * 5)
