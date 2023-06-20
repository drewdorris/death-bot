import requests
import time
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime

olddeadpeople = []

# this method is kind of unnecessary but it cleans up things a bit
# just prints the death message and calls the image searcher
def handle_death(death):
    print(datetime.now(), death)

    get_image(death)

def get_image(death):
    url = "https://www.google.com/search?q="+searchtext+"&source=lnms&tbm=isch"
    driver = webdriver.Firefox()
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
        img_count += 1
        img_url = img.get_attribute('src')
        img_type = "jpg"
        #print ("Downloading image", img_count, ": ", img_url)
        try:
            if img_type not in extensions:
                img_type = "jpg"
            req = urllib.request.Request(img_url, headers=headers)
            raw_img = urllib.request.urlopen(req).read()
            f = open(download_path+death.replace(" ", "_")+"."+img_type, "wb")
            f.write(raw_img)
            f.close
        except Exception as e:
            print("Download failed:", e)
        finally:
            print
            break
    resize_images(death)

def resize_images(name):
    print("Converting image...")
    time.sleep(2)
    for file in glob.glob("dataset\\" + name.replace(" ", "_") + "\\*.jpg"):
        i = Image.open(file);
        i = i.resize((500, 400))
        i = i.convert('RGB')
        i.save(file)

# adding path to geckodriver to the OS environment variable
# assuming that it is stored at the same path as this script
# this is for the image searching stuff
os.environ["PATH"] += os.pathsep + os.getcwd()

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
                print('whaa', x)
                continue
            handle_death(x)
    
    olddeadpeople = deadpeople
    time.sleep(60 * 5)
