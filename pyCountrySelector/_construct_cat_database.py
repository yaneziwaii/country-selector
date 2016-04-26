# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
dir_source = "data_src"
dir_outcome = "data"

locale_select=['en-GB','my', 'zh-Hant'] # Can be extended in the future  'zh-Hant-HK', 'zh-Hant-MO', 'zh-Hans', 'zh-Hans-SG'

import os.path, glob
import json
import requests
import icu # pip install PyICU

## Retrive data directly from unicode-cldr project hosted at github

URL_CLDR_JSON_TERRITORIES = "https://raw.githubusercontent.com/unicode-cldr/cldr-localenames-full/master/main/{locale}/territories.json"

locale_json={}
for l in locale_select:
    url = URL_CLDR_JSON_TERRITORIES.format(locale=l)
    r = requests.get(url)
    if r.status_code == 200:
        locale_json [l] = r.json()['main'][l]['localeDisplayNames']['territories']

## Preprocessing and Generating lists

ITEM_NAME_CODE = "{name}[{code}]"
ITEM_CODE_NAME = "{code}:{name}"

outputlist_territories={}
for key, value in locale_json.items():
    ### Remove UN regional codes (three digits)  
    value_new = {k: v for k, v in value.items() if k.isdigit() is not True}

    ### Generate items for different group of lists
    n_c=[]
    c_n=[]
    for k, v in value_new.items():
        ### Remove -alt-variant and -alt-short
        if len(k)>2:
            k = k.replace("-alt-variant","")
            k = k.replace("-alt-short","")
        n_c.append(ITEM_NAME_CODE.format(name=v, code=k))
        c_n.append(ITEM_CODE_NAME.format(name=v, code=k))
   
    ### Sort by IBM's ICU library, which uses the full Unicode Collation Algorithm
    print (key)
    collator = icu.Collator.createInstance(icu.Locale('{lc}.UTF-8'.format(lc=key)))
    n_c = sorted(n_c, key=collator.getSortKey )
    c_n = sorted(c_n, key=collator.getSortKey )

    outputlist_territories [key]  = n_c + c_n


## Outpuing Lists
outputfilename = "territories.json"
for lc, outputlist in outputlist_territories.items():

    ### Create directory if not exists
    directory = os.path.join("..", dir_outcome, lc)
    if not os.path.exists(directory):
        os.makedirs(directory)

    outputfilename = os.path.join (directory, "territories.json")
    with open(outputfilename, 'w', encoding="utf-8") as outfile:
        outfile.write("{}".format(outputlist))
        #json.dump("{}".format(outputlist), outfile)

