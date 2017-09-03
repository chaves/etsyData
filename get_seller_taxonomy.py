#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 11:11:14 2017

@author: Bruno Chaves
"""

import pandas as pd
from classes.EtsyApi import EtsyApi

etsy = EtsyApi()

OUTPUT_PATH = '_outputs/'


def make_data_frame():
    df = pd.DataFrame()
    categories = etsy.get_seller_taxonomy()  # get the taxonomy from Etsy as json
    for l1 in categories:
        l1_id = l1['category_id']
        l1_cat_name = l1['name']
        l1_path = l1['path']

        for l2 in l1['children']:
            l2_id = str(l2['id'])
            l2_name = l2['name']
            l2_path = l2['path']

            for l3 in l2['children']:
                l3_id = str(l3['id'])
                l3_name = l3['name']
                l3_path = l3['path']
                
                df = df.append({
                    'l1_id': l1_id,
                    'l1_cat_name': l1_cat_name,
                    'l1_path': l1_path,
                    'l2_id': l2_id,
                    'l2_name': l2_name,
                    'l2_path': l2_path,
                    'l3_id': l3_id,
                    'l3_name': l3_name,
                    'l3_path': l3_path
                                }, ignore_index=True)
    return df

output_df = make_data_frame()
output_df.to_excel(OUTPUT_PATH + 'seller_taxonomy_{}.xlsx'.format(etsy.get_date_now()), index=False, header=True)
