#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  2 08:47:19 2017

Vérifie quels sont les chemins actifs pour chaque catégorie filtrée par le pays.
Les catégories vides retournent un 404.

Remarque : Le filtre du pays joue ici un rôle.
En effet, une page retournant 404 avec ce filtre peut retourner un 200 sans.

"""

from classes.EtsyScraping import EtsyScraping
import pandas as pd
import time

es = EtsyScraping()

df = pd.read_excel('_output/shops.xlsx')
tempo_list = []

for path in df.l3_path:
    time.sleep(3)
    url = es.make_category_link(path)
    status = es.check_status(url)
    tempo_list.append(status)
    print('{} : {}'.format(status, url))

df['status'] = tempo_list
df.to_excel('_output/shops.xlsx', index=False, header=True)