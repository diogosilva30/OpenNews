import datetime
from functools import wraps
import json
from datetime import time
from datetime import datetime
from datetime import timedelta

from flask import Flask, jsonify, request, make_response, abort, url_for
import jwt
import requests
from db import Database

from rq import Queue
from rq.job import Job
from worker import conn

import Publico

app = Flask(__name__)
# Following line decides if json keys get ordered or not (Default is True)
app.config["JSON_SORT_KEYS"] = False
app.config['SECRET_KEY'] = 'did you knows unicorns eat their cereals at full moon?'
app.config['APPLICATION_ROOT'] = '/api/'
db = Database()
q = Queue(connection=conn)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')  # passed in query string args

        if not token:
            # bad request
            return jsonify({'status': 'error', 'message': 'Token is missing'}), 401

        try:
            _ = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            # bad request
            return jsonify({'status': 'error', 'message': 'Token is invalid'}), 401

        return f(*args, **kwargs)
    return decorated


@app.route('/')
def home():
    return 'hello world!'


@app.route('/api/login')
def login():
    auth = request.authorization

    if auth and auth.username == 'admin' and auth.password == '1234':
        token = jwt.encode({'user': auth.username, 'exp': datetime.utcnow(
        ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    # {'WWW-Authenticate': 'Basic realm="Login Required"'} --> this makes login prompt show up
    return jsonify({"status": 'error', 'message': 'Could not verify the credentials'}), 401


@app.route('/api/news', methods=['GET'])
@token_required
def get_news():

    jornal_name = request.args.get('jornal_name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search_word = request.args.get('search_word')

    if search_word is None or jornal_name is None:
        abort(400)

    if jornal_name == "publico":
        from app import get_news_from_publico
        job = q.enqueue_call(
            func=get_news_from_publico, args=(
                search_word, start_date, end_date,), result_ttl=5000
        )
        return jsonify({"status": "ok", "message": "Your job has been added to the queue!", "job id": job.get_id(), "Content URL": url_for('get_result', job_key=job.get_id(), _external=True)})
    # elif jornal_name == "cm":
        # data = get_news_from_cm()
    else:
        abort(404)

    # return jsonify({"status": "ok", "URI": url_for('get_news', _external=True), "total_news": len(data), "data": json.loads(json.dumps(data, default=serialize_list))})


@app.route("/api/results/<job_key>/", methods=['GET'])
def get_result(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = db.GetOne_By_Data(json.loads(
            json.dumps(job.result, default=serialize_list)))
        return jsonify({"status": "ok", "URI": url_for('get_news', _external=True), "data": json.loads(result)})
    else:
        return make_response(jsonify({'message': "This job has not been processed yet, try again later!"}), 202)


"""
Error handling
"""


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


"""
Functions
"""


def serialize_list(obj):
    if isinstance(obj, (datetime, time)):
        return obj.isoformat()

    elif hasattr(obj, '__dict__'):
        return obj.__dict__


def get_news_from_publico(search_word, start_date=None, end_date=None):
    print('Starting to search news from Público with search word "' + search_word + '"')
    search_word = search_word.replace(" ", "-")
    # Variable to hold the current page number
    page = 1
    news_objects = []

    while (r := requests.get("https://www.publico.pt/api/list/" +
                             search_word.lower() + "?page=" + str(page))).text != "[]":
        # Log the current search page
        print("Reading page " + str(page))
        # Read the json data
        data = json.loads(r.text)

        processed_data, search_stop = process_data(
            data, news_objects, start_date, search_word)

        news_objects.extend(processed_data)
        if search_stop:
            break  # stop the search

        page = page+1

    # Remove news greater than end date
    if end_date is not None:
        print("Now removing news which date is greater than upper bound...")
        news_objects = [
            item for item in news_objects if item.data < Publico.from_datetime(end_date)]

    # Complete the news with corpus
    get_corpus(news_objects)

    # Persist the results
    try:
        result_str = json.dumps(news_objects, default=serialize_list)
        db.AddToDb(result_str)
    except:
        print("Unable to add item to database!")
        abort(500)


def process_data(data, news_objects, start_date, search_word):
    # Transform the list data into a dict
    new_dict = {}
    new_dict = {item['id']: item for item in data}
    # Create array for processed data
    processed_data = []
    # Flag to stop the search
    stop_entire_search = False

    for key, value in new_dict.items():
        try:
            if value not in news_objects:
                processed_data.append(Publico.Publico_From_Dict(
                    s=value, start_date=start_date, search_key=search_word))
            else:
                print("News with id " + str(value.get("id")) +
                      " was already in list! Skipping...")
        except ValueError:
            print("Found news out of lower bound date, stopping the search...")
            stop_entire_search = True
            break  # stop the local search

    # Remove 'None' values in list
    processed_data = list(filter(None, processed_data))

    return processed_data, stop_entire_search


def get_corpus(data):
    urls = []
    for item in data:
        urls.append(item.url)
    news_corpus = Publico.get_news_corpus(urls)
    i = 0
    for item in data:
        item.texto = news_corpus[i]
        i = i+1

    return data


if __name__ == '__main__':
    app.run(debug=True)
