#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:09:15 2017

@author: Bruno Chaves

This file scrapes all shops names and product ids by navigating
from the categories paths in the shops.xlsx file

"""

from classes.EtsyScraping import EtsyScraping
import pandas as pd
import json

STEPS_MAX = 10
CATEGORIES_CONTROL_FILE = '_outputs/categories_control.xlsx'
OUTPUT_PATH = '_outputs/shops_products/'
step = 0

while step < STEPS_MAX:

    es = EtsyScraping()

    df = pd.read_excel(CATEGORIES_CONTROL_FILE)
    
    idx = df[(df['shops'] == 0) & (df['status'] == 200)].head(1).index
    
    if idx.empty:
        print('Finished !')
        break
    
    else:
        
        path = list(df.loc[idx, 'l3_path'])[0]
        
        data = es.get_shops_and_product_ids_from_category(path)
        file_name = OUTPUT_PATH + path + '.json'
        
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)
            
        df.loc[idx, 'pages_total'] = es.get_pages_total()
        df.loc[idx, 'shops'] = 'OK'
        
        df.to_excel(CATEGORIES_CONTROL_FILE, index=False, header=True)

    step += 1
    print('Step :{}'.format(step))