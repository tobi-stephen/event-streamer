from proxy import db, app
from kafka_service import KafkaService
import searchclients
import common

import uuid
import datetime
import threading

from flask import jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token


kafkaClient = KafkaService()


def register_user(data: dict):
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password or not email:
        return jsonify({'status': 'failure', 'message': 'missing field'}), 400
    
    now = str(datetime.datetime.now())
    user_id = str(uuid.uuid4())
    user = {
        'user_id': user_id,
        'username': username,
        'email': email,
        'password': generate_password_hash(password),
        'date_created': now,
        'date_modified': now
    }

    try:
        db.users.insert_one(user)
    except Exception as e:
        (e)
        return jsonify({'status': 'failure', 'message': str(e)}), 400
    
    return jsonify({'status': 'success', 'message':'user registered'}), 201


def login_user(data: dict):
    username = data.get('username')
    password = data.get('password')

    existing_user = db.users.find_one({'username': username})
    if not existing_user or not check_password_hash(existing_user.get('password'), password):
        return jsonify({'status': 'failure', 'message': 'username/password invalid'}), 401
    
    access_token = create_access_token(identity={'username': username, 'user_id': existing_user.get('user_id')})

    # TODO: use a queue for this later
    def update_user_last_login(username):
        app.logger.info('updating last login for: ', username)
        now = str(datetime.datetime.now())
        db.users.update_one({'username': username}, {'$set': {'last_login_date': now}})

    threading.Thread(target=update_user_last_login, args=(username,)).start()

    return jsonify({'status': 'success', 'message': 'login ok', 'data': access_token})

    
def get_user_profile(session_data: dict):
    username = session_data.get('username')

    existing_user = db.users.find_one({'username': username}, projection={'_id':0, 'password': 0})
    if not existing_user:
        return jsonify({'status': 'failure', 'message': 'invalid user session'}), 401

    return jsonify({'status': 'success', 'message': 'profile found', 'data': existing_user})


def create_event(session_data, data: dict):
    # verify data
    title = data.get('title')
    details = data.get('details')

    if not title or not details:
        return jsonify({'status': 'failure', 'message': 'missing field'}), 400
    
    # get user details
    user = db.users.find_one({'username': session_data.get('username')})
    if not user:
        return jsonify({'status': 'failure', 'message': 'invalid user session'}), 401
    
    event_id = str(uuid.uuid4())
    now = str(datetime.datetime.now())
    event = {
        'event_id': event_id,
        'created_by': user.get('user_id'),
        'title': title,
        'details': details,
        'date_created': now,
        'date_modified': now
    }

    try:
        db.events.insert_one(event)
        event.pop('_id')
        event.pop('created_by')
    except Exception as e:
        app.logger.info(e)
        return jsonify({'status': 'failure', 'message': 'event creation issue'}), 400
    
    threading.Thread(target=kafkaClient.produce_idea_event, args=(event_id, event)).start()
    
    return jsonify({'status': 'success', 'message': 'event created', 'data': event_id}), 201


def update_event(session_user, event_id, data):
    pass


def fetch_event_by_id(event_id):

    # fetching the event even if not created by user in session data
    event = db.events.find_one({'event_id': event_id}, projection={'_id': 0, 'created_by': 0})
    if not event:
        return jsonify({'status': 'failure', 'message': 'invalid event'}), 400
    
    return jsonify({'status': 'success', 'message': 'event found', 'data': event})


def fetch_events_paged(limit, page, user_id=None):
    limit = int(limit or '10')
    page = int(page or '1')

    if user_id:
        events = list(
            db.events.find({'created_by': user_id}, projection={'_id': 0, 'created_by': 0}).skip(page).limit(limit)
        )
    else:
        events = list(
            db.events.find({}, projection={'_id': 0, 'created_by': 0}).skip(page).limit(limit)
        )

    if not events:
        message = 'no events found'
    else:
        message = 'events found'

    return jsonify({'status': 'success', 'message': message, 'data': events})


def search_events(limit, page, query):
    # this routine will fetch events from elasticsearch/opensearch based on 'query'
    limit = int(limit or '10')
    page = int(page or '1')
    query = query or ''

    import os
    search_provider = searchclients.providers.get(os.getenv('SEARCH_PROVIDER') or 'elastic')
    es: searchclients.Search = search_provider(index=common.EVENT_IDEA_INDEX)

    # query expression to match texts(part or full) with 'title' or 'details' field of 'events'
    # https://stackoverflow.com/questions/52493339/elasticsearch-one-regexp-for-multiple-fields
    query_exp = '.*' + query + '.*'
    q = {  # TODO: might need to adjust this query if using opensearch
        'query': {
            'bool': {
                'should': [
                    {
                        'regexp': {
                            'title': {
                                'value': query_exp,
                                'flags': 'ALL',
                                'case_insensitive': True,
                                'max_determinized_states': 10000,
                                'rewrite': 'constant_score_blended'
                            }
                        }
                    },
                    {
                        'regexp': {
                            'details': {
                                'value': query_exp,
                                'flags': 'ALL',
                                'case_insensitive': True,
                                'max_determinized_states': 10000,
                                'rewrite': 'constant_score_blended'
                            }
                        }
                    }
                ]
            }
        }
    }

    results = es.search(query_args=q)
    results=results['hits']['hits']
    return jsonify({'status': 'success', 'message': 'events found', 'data': results})
