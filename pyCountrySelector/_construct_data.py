# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
dir_outcome = "data"
## Outpuing Lists
outputfn_locales = "locales_available.json"
outputfn_src_lc = "territories.json"
outputfn_JSON = "territories.json"
outputfn_HTML = "territories_snippet.htm"

import os.path, glob
import json
import requests
import icu # pip install PyICU

def url_request (url):
    r = requests.get(url)
    if r.status_code == 200:
        return r
    else:
        return None 


def load_json_list (lc_file, u):
    try:
        with open(lc_file, 'r', encoding="utf-8") as infile:
            _select = json.load (infile)
            print ("Loaded from local file.")
    except:
        results = url_request (url  = u)
        if results is not None:
            try:
                _select = results.json()['availableLocales']['full']
                with open(lc_file, 'w', encoding="utf-8") as outfile:
                    outfile.write("{}".format(_select).replace("'",'"'))
                print ("Loaded from designated url.")
            except:
                pass
    return _select

# Full Construction
URL_CLDR_JSON_AVAIL_LOCALES_LC = os.path.join ("..", dir_outcome, outputfn_locales)
URL_CLDR_JSON_AVAIL_LOCALES = "https://raw.githubusercontent.com/unicode-cldr/cldr-core/master/availableLocales.json"
locale_select = load_json_list (URL_CLDR_JSON_AVAIL_LOCALES_LC, URL_CLDR_JSON_AVAIL_LOCALES)

# Partial Selected Construction
#locale_select = ['en-GB','my', 'zh-Hant'] # Can be extended in the future  'zh-Hant-HK', 'zh-Hant-MO', 'zh-Hans', 'zh-Hans-SG'

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
    n_c_full_data=[]
    n_c_data=[]
    c_n_data=[]
    #r_n=dict()  #region--names

    c_n=dict()
    for k, v in value_new.items():
        
        ## n_c_full_data are complete list
        n_c_full_data.append(ITEM_NAME_CODE.format(name=v, code=k))    

        ### Remove -alt-variant and -alt-short
        if len(k)>2:
            if "-alt-variant" in k:
                #print (">NOT using:{}".format([k,v]))
                pass
            if "-alt-short" in k:  ## Using -alt-short if exists
                k=k.replace("-alt-short", "")
                print (">    using:{}".format([k,v]))
                c_n.update({k:v})
            #if len(k)==3 and k.isdigit():
            #    r_n.update({k:v})  ## UN region codes
            
        else:
            if k not in c_n.keys():
                c_n.update({k:v})
            else:
                print (">NOT using:{}".format([k,v]))

    for k,v in c_n.items():
        n_c_data.append(ITEM_NAME_CODE.format(name=v, code=k))
        c_n_data.append(ITEM_CODE_NAME.format(name=v, code=k))
   
    ### Sort by IBM's ICU library, which uses the full Unicode Collation Algorithm
    print (key)
    collator = icu.Collator.createInstance(icu.Locale('{lc}.UTF-8'.format(lc=key)))
    n_c_data = sorted(n_c_data, key=collator.getSortKey )
    c_n_data = sorted(c_n_data, key=collator.getSortKey )

    outputlist_territories [key]  = n_c_data + c_n_data


## Outpuing Lists
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

