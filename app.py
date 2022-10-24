from multiprocessing.sharedctypes import Value
from re import A
import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, make_response
from cleansing import  process_text, process_csv
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

#BACA DATABASE
db = sqlite3.connect('dbc.db', check_same_thread=False) 
db.row_factory = sqlite3.Row
mycursor = db.cursor()

# KONFIGURASI FLASK SWAGGER
SWAGGER_URL = '/index'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Challenge Gold Data Science Binar Academy"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.route('/', methods=['GET'])
def get():
    return "Welcome to My Cleansing API"

@app.route("/tweet", methods=["GET"])
def tweet():
    query = "select * from tweet"
    tweet = mycursor.execute(query)
    tweet = [
            dict(id=row[0], tweet_old=row[1], tweet_cleaned=row[2])
            for row in tweet.fetchall()
        ]
    return jsonify(tweet)

@app.route("/tweet", methods=["POST"])
def post_tweet():
    tweet_baru = str(request.form["text"])
    cleansing = process_text(tweet_baru)
    query_text = "insert into tweet (tweet_old,tweet_cleaned) values (?,?)"
    value=(tweet_baru,cleansing)
    mycursor.execute(query_text, value)
    db.commit()
    return f"{value} berhasil diinput"

@app.route("/tweet/<string:id>", methods=["GET"])
def get_id(id):
    query = "select * from tweet where id = ?"
    id = str(id)
    tweet = mycursor.execute(query, [id])
    cari_tweet = [
        dict(id=row[0], tweet_old=row[1], tweet_cleaned=row[2])
        for row in tweet.fetchall()
    ]

    return jsonify(cari_tweet)

@app.route("/tweet/<string:id>", methods=["PUT"])
def put_id(id):
    tweet_update = str(request.form["text"])
    cleansing = process_text(tweet_update)
    query = "update tweet set tweet_old = ?, tweet_cleaned = ? where id = ?"
    value = (tweet_update, cleansing, id)
    mycursor.execute(query, value)
    db.commit()
        
    return f"Isi Tweet {id} Berhasil Diupdate dan Diclean"

@app.route("/tweet/<string:id>", methods=["DELETE"])
def del_id(id):
    query = "delete from tweet where id = ?"
    mycursor.execute(query, [id])
    db.commit()
    return f"Tweet {id} Berhasil Dihapus"
          
# Upload CSV File
@app.route("/tweet/csv", methods=["POST"])
def tweet_csv():
    file = request.files['file']
    try:
        data = pd.read_csv(file, encoding='iso-8859-1')
    except:
        data = pd.read_csv(file, encoding='utf-8') 
    process_csv(data)
    return "DONE"



# error handling
@app.errorhandler(400)
def handle_400_error(_error):
    "Return a http 400 error to client"
    return make_response(jsonify({'error': 'Misunderstood'}), 400)


@app.errorhandler(401)
def handle_401_error(_error):
    "Return a http 401 error to client"
    return make_response(jsonify({'error': 'Unauthorised'}), 401)


@app.errorhandler(404)
def handle_404_error(_error):
    "Return a http 404 error to client"
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def handle_500_error(_error):
    "Return a http 500 error to client"
    return make_response(jsonify({'error': 'Server error'}), 500)

if __name__ == '__main__':
    app.run()