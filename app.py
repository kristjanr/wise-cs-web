import datetime
import urllib
import uuid
from collections import defaultdict
from flask_cors import CORS, cross_origin
import psycopg2
import json

from flask import Flask, request, session, make_response
import os
import secrets

from agent.agent import respond
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
origins = ["http://localhost:3000", "https://wise-ai-help.herokuapp.com"]
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
@app.route("/answer")
def answer():
    set_session_if_needed()
    session_id = session['ID']
    question = request.args.get('question')
    previous_messages = get_previous_messages(session_id)
    previous_questions = get_previous_questions(session_id)

    llm_answer, urls, new_messages = respond(question, previous_messages, previous_questions)

    questions = previous_questions.copy()
    questions.append(question)

    messages = previous_messages.copy()
    messages.extend(new_messages)

    save_to_database(session_id, question, llm_answer, urls, messages, questions)

    print(f'Question: {question}, Answer: {llm_answer}, Articles used: {"/n".join(urls)}"')
    return dict(answer=llm_answer, urls_used=urls)


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
    '''
    with conn.cursor() as cursor:
        cursor.execute(insert_query, (session_id, question, llm_answer, json.dumps(urls), json.dumps(messages), json.dumps(questions)))
        conn.commit()


def set_session_if_needed():
    if session.get('ID') is None:
        print("ID puudus")
        session['ID'] = str(uuid.uuid4())
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=1)
        response = make_response()
        response.set_cookie("session_id", session["ID"], expires=expiry_date)
        return
    print("ID oli olemas")
    print(session['ID'])


# TODO: when session exists, load the previous messages and questions - this needs saving them to DB
# Add a feedback button to the UI & save the feedback to DB with the question and answer
# Add a token counter and warn the user when they are running out of tokens & ask to reset the session
# Test if multithreading works with sessions etc
# Copy from bing - notify when context window gets full and recommend to reset session
# Add a feedback modal to the UI - thumbs up, neutral, thumbs down, plus a text field for comments.
