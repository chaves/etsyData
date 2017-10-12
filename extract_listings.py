import glob
import os.path
import json
import pandas as pd
import time
import datetime
import re
from ftfy import fix_text

# Max number of files to process
FILES_MAX = 250
FILE_WITH_POCESSED_SHOPS = '_outputs/controls/proceeded_shops.txt'
FILE_PROCESS_DURATIONS = '_outputs/controls/process_shops_durations.txt'

columns = ['listing_id', 'state', 'user_id', 'shop_id', 'page', 'category_id', 'title', 'description',
        'creation_date', 'ending_date', 'original_creation_date', 'last_modified_date',
        'price', 'currency_code', 'quantity', 'tags', 'materials',
        'shop_section_id', 'url', 'views', 'num_favorers', 'who_made', 'is_supply',
        'when_made', 'is_customizable', 'is_digital', 'language', 'has_variations',
        'taxonomy_id', 'used_manufacturer']
df = pd.DataFrame(columns=columns)

def append_to_csv_void(df, csvFilePath, sep=","):
    import os
    if not os.path.isfile(csvFilePath):
        df.to_csv(csvFilePath, mode='a', index=False, sep=sep)
    elif len(df.columns) != len(pd.read_csv(csvFilePath, nrows=1, sep=sep).columns):
        raise Exception(
            "Columns do not match!! Dataframe has " + str(len(df.columns)) + " columns. CSV file has " + str(
                len(pd.read_csv(csvFilePath, nrows=1, sep=sep).columns)) + " columns.")
    elif not (df.columns == pd.read_csv(csvFilePath, nrows=1, sep=sep).columns).all():
        raise Exception("Columns and column order of dataframe and csv file do not match!!")
    else:
        df.to_csv(csvFilePath, mode='a', index=False, sep=sep, header=False)

def fix_text2(text):
    if type(text) is str:
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = re.sub(' +', ' ', text)
        return fix_text(text.rstrip())
    return None


def check_key(key, source):
    if key in source.keys():
        return source[key]
    else:
        return 'NaN'

def check_key_date(key, source):
    if key in source.keys():
        return datetime.datetime.fromtimestamp(int(source[key])).strftime('%Y-%m-%d')
    else:
        return 'NaN'


def get_row(data, shop_id, page):
    d = data

    listing_id = str(check_key('listing_id', d))
    state = check_key('state', d)
    user_id = str(check_key('user_id', d))
    shop_id = shop_id
    page = page
    category_id = str(check_key('category_id', d))
    title = fix_text2(check_key('title', d))
    description = fix_text2(check_key('description', d))

    creation_date = check_key_date('creation_tsz', d)
    ending_date = check_key_date('ending_tsz', d)
    original_creation_date = check_key_date('original_creation_tsz', d)
    last_modified_date = check_key_date('last_modified_tsz', d)

    price = check_key('price', d)
    currency_code = check_key('currency_code', d)
    quantity = str(check_key('quantity', d))
    tags = str(check_key('tags', d))
    materials = str(check_key('materials', d))
    shop_section_id = str(check_key('shop_section_id', d))
    url = check_key('url', d).replace('https://www.etsy.com/', '')
    views = str(check_key('views', d))
    num_favorers = str(check_key('num_favorers', d))
    who_made = check_key('who_made', d)
    is_supply = check_key('is_supply', d)
    when_made = check_key('when_made', d)
    is_customizable = str(check_key('is_customizable', d))
    is_digital = str(check_key('is_digital', d))
    language = check_key('language', d)
    has_variations = str(check_key('has_variations', d))

    taxonomy_id = str(check_key('taxonomy_id', d))
    used_manufacturer = str(check_key('used_manufacturer', d))

    row = [listing_id, state, user_id, shop_id, page, category_id, title, description,
           creation_date, ending_date, original_creation_date, last_modified_date,
           price, currency_code, quantity, tags, materials,
           shop_section_id, url, views, num_favorers, who_made, is_supply,
           when_made, is_customizable, is_digital, language, has_variations,
           taxonomy_id, used_manufacturer]
    return row


def get_pocessed_files(file):
    if not os.path.exists(file):
        open(file, 'w')
        return []
    else:
        with open(file) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            return content


source_list = glob.glob("_outputs/shops_listings/*.json")
source_list = sorted(source_list)

# Total source files
print('Total number of source files {} '.format(len(source_list)))

pocessed_list = get_pocessed_files(FILE_WITH_POCESSED_SHOPS)
# Total pocessed files
print('Total number of processed files {} '.format(len(pocessed_list)))

if len(pocessed_list) > 0:
    files_to_process = [file for file in source_list if file not in pocessed_list]
else:
    files_to_process = source_list
    open(FILE_WITH_POCESSED_SHOPS, 'w')

files_to_process = files_to_process[:FILES_MAX]

# Total pocessed files
print('Total number of files to process {} '.format(len(files_to_process)))

time.sleep(2)

file_number = 0
durations = []
for file_name in files_to_process:
    # start = datetime.datetime.now()
    shop_id = file_name.split('/')[-1].split('_')[0]
    page = file_name.split('_')[-1].split('.')[0]
    file_number += 1
    print('File {}'.format(file_name.split('/')[-1]))
    print('Number {}'.format(file_number))
    with open(file_name, 'r') as f:
        data = json.load(f)
        if type(data) == dict and 'results' in data.keys() and len(data['results']) > 0:
            items = data['results']
            for item in items:
                df.loc[len(df)] = get_row(item, shop_id, page)
    # duration = datetime.datetime.now() - start
    # durations.append(duration)

# with open(FILE_PROCESS_DURATIONS, 'w') as f:
#     for item in durations:
#         f.write("%s\n" % item)

append_to_csv_void(df, '_outputs/listings.csv', sep="|")

with open(FILE_WITH_POCESSED_SHOPS, 'a') as f:
    for item in files_to_process:
        f.write("%s\n" % item)
