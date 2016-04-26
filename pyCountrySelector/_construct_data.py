# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
dir_source = "data_src"
dir_outcome = "data"

import os.path, glob
import json
import requests
import icu # pip install PyICU

def url_request(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r
    else:
        return None 

# Partial Selected Construction
locale_select=['en-GB','my', 'zh-Hant'] # Can be extended in the future  'zh-Hant-HK', 'zh-Hant-MO', 'zh-Hans', 'zh-Hans-SG'

# Full Construction
URL_CLDR_JSON_AVAIL_LOCALES = "https://raw.githubusercontent.com/unicode-cldr/cldr-core/master/availableLocales.json"
results = url_request (url  = URL_CLDR_JSON_AVAIL_LOCALES)
if results is not None:
    try:
        locale_select = results.json()['availableLocales']['full']
    except:
        pass

## Retrive data directly from unicode-cldr project hosted at github
print ("Retrieve data now ...")
URL_CLDR_JSON_TERRITORIES = "https://raw.githubusercontent.com/unicode-cldr/cldr-localenames-full/master/main/{locale}/territories.json"
locale_json={}
for l in locale_select:
    results = url_request (url  = URL_CLDR_JSON_TERRITORIES.format(locale=l))
    if results is not None:
        try:
            locale_json [l] = results.json()['main'][l]['localeDisplayNames']['territories']
        except:
            pass

## Preprocessing and Generating lists
print ("Preprocessing data now ...")
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
outputfn_JSON = "territories.json"
outputfn_HTML = "territories_snippet.htm"

for lc, outputlist in outputlist_territories.items():
    ### Create directory if not exists
    directory = os.path.join("..", dir_outcome, lc)
    if not os.path.exists(directory):
        os.makedirs(directory)
    outputfn_json = os.path.join (directory, outputfn_JSON)
    outputfn_html = os.path.join (directory, outputfn_HTML)
    
    with open(outputfn_json, 'w', encoding="utf-8") as outfile:
        outfile.write("{}".format(outputlist).replace("'",'"'))
        #json.dump("{}".format(outputlist), outfile)
    with open(outputfn_html, 'w', encoding="utf-8") as outfile:
        outputtxt = '''<datalist id="countries">'''+"".join(['''<option value="{v}">'''.format(v=x) for x in outputlist])+'''</datalist>'''
        outfile.write(outputtxt)

