
from proxy import app
import services

import datetime
from flask import jsonify, request, g
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

@app.route('/')
@app.route('/health')
def index():
    return jsonify({'status': 'ok'})


@app.post('/register')
def register():
    return services.register_user(data=request.json)


@app.post('/login')
def login():
    return services.login_user(data=request.json)


@app.get('/user/profile')
@jwt_required()
def get_user_profile():
    session_user = get_jwt_identity()
    return services.get_user_profile(session_user)


@app.post('/events')
@jwt_required()
def create_event():
    session_user = get_jwt_identity()
    return services.create_event(session_user, data=request.json)


@app.get('/events/<event_id>')
def fetch_event(event_id):
    return services.fetch_event_by_id(event_id)


@app.put('/events/<event_id>')
@jwt_required()
def update_event(event_id):
    session_user = get_jwt_identity()
    return services.update_event(session_user, event_id, data=request.json)


@app.get('/events')
def fetch_events_paged():
    limit = request.args.get('limit')
    page = request.args.get('page')
    user_id = request.args.get('user_id')
    return services.fetch_events_paged(limit, page, user_id)


@app.get('/events/search')
def search_similar_events():
    limit = request.args.get('limit')
    page = request.args.get('page')
    query = request.args.get('query')
    return services.search_events(limit, page, query)


@app.before_request
def handle_request():
    g.request_time = datetime.datetime.now()


@app.after_request
def handle_response(response):
    diff: datetime.timedelta = datetime.datetime.now() - g.request_time
    app.logger.info(f'request took {diff.total_seconds()} seconds')
    return response


@app.errorhandler(Exception)
def handle_exceptions(e: Exception):
    app.logger.error(e)
    return jsonify({'status': 'failure', 'message': str(e)}), 400