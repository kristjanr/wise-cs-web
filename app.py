import datetime
import urllib
import uuid
from collections import defaultdict
from flask_cors import CORS, cross_origin
import psycopg2
import json
import openai
from flask import Flask, request, session, make_response
import os
import secrets

from agent.agent import respond
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'development':
    print('Using development config')
else:
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_DOMAIN='qryys7e88c.execute-api.eu-north-1.amazonaws.com'
    )
    print('Using production config')

origins = ["http://localhost:3000/", "https://wise-ai-help.herokuapp.com", "https://qryys7e88c.execute-api.eu-north-1.amazonaws.com/api"]
CORS(app, origins=origins, supports_credentials=True)

secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

message_history = defaultdict(list)
question_history = defaultdict(list)

if 'DATABASE_URL' not in os.environ:
    raise Exception('DATABASE_URL environment variable not set')
# Parse the Heroku DATABASE_URL
url = urllib.parse.urlparse(os.environ['DATABASE_URL'])

# Set up connection to PostgreSQL database
conn = psycopg2.connect(
    host=url.hostname,
    database=url.path[1:],
    user=url.username,
    password=url.password
)


@cross_origin()
@app.route('/feedback', methods=['POST'])
def feedback():
    session_existed_already = set_session_if_needed()
    if not session_existed_already:
        return 'No session exists', 400
    session_id = session['ID']
    request_data = request.get_json()
    row_id = request_data['messageId']
    select_query = '''
        SELECT session_id FROM session_history
        WHERE id = %s AND session_id = %s AND is_good_feedback IS NULL
    '''
    with conn.cursor() as cursor:
        cursor.execute(select_query, (row_id, session_id))
        result = cursor.fetchone()
        if result is None:
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
    return 'Success', 200


@cross_origin()
@app.route('/logout')
def logout():
    resp = make_response("Cookie Removed")
    resp.set_cookie('session', '', expires=0)
    return resp


@cross_origin()
@app.route("/answer")
def answer():
    session_existed_already = set_session_if_needed()
    session_id = session['ID']
    question = request.args.get('question')
    previous_messages = []
    previous_questions = []
    if session_existed_already:
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


def set_session_if_needed():
    if session.get('ID') is None:
        print("ID puudus")
        session['ID'] = str(uuid.uuid4())
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=1)
        response = make_response()
        response.set_cookie("session_id", session["ID"], expires=expiry_date)
        return False
    print("ID oli olemas")
    print(session['ID'])
    return True

# TODO: when session exists, load the previous messages and questions - this needs saving them to DB
# Add a feedback button to the UI & save the feedback to DB with the question and answer
# Add a token counter and warn the user when they are running out of tokens & ask to reset the session
# Test if multithreading works with sessions etc
# Copy from bing - notify when context window gets full and recommend to reset session
# Add a feedback modal to the UI - thumbs up, neutral, thumbs down, plus a text field for comments.
