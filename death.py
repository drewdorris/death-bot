import requests
import time
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime

olddeadpeople = []

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
            if len(x) > 2:
                if x[1].isdigit():
                    if x[0] == 'Q':
                        print('whaaaa')
                        print(x)
                        continue
            now = datetime.now() # get the actual date of death? doesn't matter
            print(now)
            print(x)

    olddeadpeople = deadpeople
    time.sleep(60 * 5)
