import pandas as pd
import re
import sqlite3

#BACA DATABASE
db = sqlite3.connect('dbc.db', check_same_thread=False)
db.text_factory = bytes
mycursor = db.cursor()

#Baca Table Abusive
abusive = "select * from abusive"
list_abusive = pd.read_sql_query(abusive, db)
list_abusive['ABUSIVE'] = list_abusive['ABUSIVE'].str.decode('utf-8')
abusive_list = list_abusive['ABUSIVE'].values.tolist()

#Baca Table Kamus Alay
query = "select * from kamus_alay"
kamusalay = pd.read_sql_query(query, db)
kamusalay['hasil clean'] = kamusalay['hasil clean'].str.decode('utf-8')
kamusalay['kata alay'] = kamusalay['kata alay'].str.decode('utf-8')

#Fungsi Clean Kata Abusive
def clean_abusive(text):
    word_list = text.split()
    return ' '.join([i for i in word_list if i not in abusive_list])

#Fungsi Clean Kamus Alay
alay_dict_map = dict(zip(kamusalay['kata alay'], kamusalay['hasil clean']))
def replace_kamus_alay(text):
    for word in alay_dict_map:
        return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])

#Ubah text menjadi lower
def lower(text):
    return text.lower()


# Hapus karakter khusus
def hapuskarakter(text):
    text = re.sub('\n',' ', text)
    text = re.sub('rt',' ', text)
    text = re.sub('user',' ', text)
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text)
    text = re.sub('  +',' ', text)
    return text

# Cleansing Data
def preprocess(text):
    text = lower(text)
    text = hapuskarakter(text)
    text = clean_abusive(text)
    text = replace_kamus_alay(text)
    return text


# Input Text
def process_text(input_text):
    try: 
        output_text = preprocess(input_text)
        return output_text
    except:
        print("Error")

# Upload File
def process_csv(input_file):
    first_column = input_file.iloc[:, 0]
    print(first_column)

    for tweet in first_column:
        tweet_clean = preprocess(tweet)
        query_tabel = "insert into tweet (tweet_old,tweet_cleaned) values (?, ?)"
        value = (tweet, tweet_clean)
        mycursor.execute(query_tabel, value)
        db.commit()
        print(tweet)