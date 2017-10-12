#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 11:11:14 2017

@author: Bruno Chaves
"""

from classes.EtsyApi import EtsyApi
import pandas as pd
import json
import time

STEPS_MAX = 1000
SHOPS_CONTROL_FILE = '_outputs/shops_products_control.xlsx'
OUTPUT_PATH = '_outputs/shops_listings/'

step = 0

while step < STEPS_MAX:

    etsy = EtsyApi()

    df = pd.read_excel(SHOPS_CONTROL_FILE)

    idx = df[df.checkedDate == 0].head(1).index

    if idx.empty:
        print('Finished !')
        break

    else:
        shop_id = idx[0]

        page = 1

        while page:

            time.sleep(6)
            print('Page : ' + str(page))

            data = etsy.get_shop_listings(shop_id, page=page)

            if data:

                file_name = OUTPUT_PATH + shop_id + '_' + str(page) + '.json'

                with open(file_name, 'w') as file:

                    json.dump(data, file, indent=4)

                page = data['pagination']['next_page']

            else:
                page = False

        df.loc[idx, 'checkedDate'] = etsy.get_date_now()

        df.to_excel(SHOPS_CONTROL_FILE, index=True, header=True)

    step += 1
    print('Step :{}'.format(step))
