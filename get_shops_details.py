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
SHOPS_CONTROL_FILE = '_outputs/shops_control.xlsx'
OUTPUT_PATH = '_outputs/shops/'

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

        data = etsy.get_shop(shop_id)

        file_name = OUTPUT_PATH + shop_id + '.json'

        with open(file_name, 'w') as file:

            json.dump(data, file, indent=4)
            df.loc[idx, 'checkedDate'] = etsy.get_date_now()

            df.to_excel(SHOPS_CONTROL_FILE, index=True, header=True)

    step += 1
    print('Step :{}'.format(step))
    time.sleep(3)
