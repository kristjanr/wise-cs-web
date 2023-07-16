import json
import os
import urllib
import uuid

import openai
import psycopg2
import redis as redis
from dotenv import load_dotenv
from flask import Flask, request, session, send_from_directory
from flask_session import Session

from agent.agent import respond

load_dotenv()

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(os.environ['REDIS_URL'])
Session(app)

if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'development':
    print('Using development config')
else:
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        REMEMBER_COOKIE_SECURE=True,
        SESSION_USE_SIGNER=True,
    )
    print('Using production config')

if 'DATABASE_URL' not in os.environ:
    raise Exception('DATABASE_URL environment variable not set')
url = urllib.parse.urlparse(os.environ['DATABASE_URL'])

# Set up connection to PostgreSQL database
conn = psycopg2.connect(
    host=url.hostname,
    database=url.path[1:],
    user=url.username,
    password=url.password
)


@app.route('/')
def serve():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


SESSION_KEY = 'sessionId'


@app.route('/feedback', methods=['POST'])
def feedback():
    session_id = session.get(SESSION_KEY)
    if not session_id:
        return 'No session exists', 400

    print(f'Session: {session.get(SESSION_KEY)}')
    request_data = request.get_json()
    row_id = request_data['messageId']
    select_query = '''
        SELECT true FROM session_history
        WHERE id = %s AND session_id = %s
    '''
    with conn.cursor() as cursor:
        cursor.execute(select_query, (row_id, session_id))
        if not cursor.fetchone():
            return 'Invalid messageId', 400

    is_good_feedback = request_data['feedback'] == 'good'
    feedback = request_data['additionalFeedback']
    update_query = '''
        UPDATE session_history
        SET is_good_feedback = %s, feedback = %s
        WHERE id = %s
    '''
    with conn.cursor() as cursor:
        cursor.execute(update_query, (is_good_feedback, feedback, row_id))
        conn.commit()
    return dict(success=True, data=request.get_json())


@app.route('/login', methods=['POST'])
def login():
    print('Logging in')
    print(f'Session: {session.get(SESSION_KEY)}')
    session[SESSION_KEY] = session.get(SESSION_KEY, str(uuid.uuid4()))
    return 'Logged in'


@app.route('/reset-session')
def logout():
    session[SESSION_KEY] = str(uuid.uuid4())
    print(f'Session reset: {session[SESSION_KEY]}')
    return 'Session reset'


@app.route('/answer')
def answer():
    session_id = session.get(SESSION_KEY)
    question = request.args.get('question')
    previous_messages = []
    previous_questions = []
    if session_id:
        print(f'Using existing session {session_id}')
        previous_messages = get_previous_messages(session_id)
        previous_questions = get_previous_questions(session_id)

    try:
        llm_answer, urls, new_messages, n_tokens_used = respond(question, previous_messages, previous_questions)
    except openai.error.InvalidRequestError as e:
        n_tokens_used = e.user_message.split('your messages resulted in ')[1].split(' tokens')[0]
        return dict(answer='Context window full. Please reset session!', urls_used=[], n_tokens_used=n_tokens_used)
    except openai.error.ServiceUnavailableError as e:
        return dict(answer='OpenAI API is currently unavailable. Please try again later.', urls_used=[],
                    n_tokens_used=0)

    questions = previous_questions.copy()
    questions.append(question)

    messages = previous_messages.copy()
    messages.extend(new_messages)

    row_id = save_to_database(session_id, question, llm_answer, urls, messages, questions)

    print(f'Question: {question}, Answer: {llm_answer}, Articles used: {"/n".join(urls)}"')
    return dict(answer=llm_answer, urls_used=urls, n_tokens_used=n_tokens_used, id=row_id)


def get_previous_questions(session_id: str) -> list:
    select_query = '''
        SELECT questions FROM session_history
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    '''
    with conn.cursor() as cursor:
        cursor.execute(select_query, (session_id,))
        result = cursor.fetchone()
        if result is None:
            return []
        else:
            return result[0]


def get_previous_messages(session_id):
    select_query = '''
        SELECT messages FROM session_history
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    '''
    with conn.cursor() as cursor:
        cursor.execute(select_query, (session_id,))
        result = cursor.fetchone()
        if result is None:
            return []
        else:
            return result[0]


def save_to_database(session_id, question, llm_answer, urls, messages, questions):
    insert_query = '''
        INSERT INTO session_history (session_id, question, llm_answer, urls, messages, questions)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    '''
    with conn.cursor() as cursor:
        cursor.execute(insert_query, (
            session_id, question, llm_answer, json.dumps(urls), json.dumps(messages), json.dumps(questions)))
        row = cursor.fetchone()
        if row:
            row_id = row[0]
            print(f'Inserted row with id {row_id}')
            conn.commit()
            return row_id
        else:
            # Handle the case where no row was returned
            print('Failed to retrieve the inserted row ID.')
            conn.rollback()
            return None
