import random
from collections import defaultdict
from flask_cors import CORS

from flask import Flask, render_template, request, session
import os
import secrets

from agent.agent import respond

app = Flask(__name__, static_folder="./frontend/build", static_url_path="/")
origins = ["http://localhost:5001", "https://wise-cs.herokuapp.com"]
CORS(app, origins=origins)

secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

message_history = defaultdict(list)
question_history = defaultdict(list)



@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route("/answer")
def answer():
    set_session_if_needed()
    question = request.args.get('question')

    previous_messages = message_history[session['ID']]
    previous_questions = question_history[session['ID']]

    llm_answer, urls, new_messages = respond(question, previous_messages, previous_questions)

    message_history[session['ID']].extend(new_messages)
    question_history[session['ID']].append(question)

    print(f'Question: {question}, Answer: {llm_answer}, Articles used: {"/n".join(urls)}"')
    return dict(answer=llm_answer, urls_used=urls)


def set_session_if_needed():
    if session.get('ID') is None:
        print("ID puudus")
        session['ID'] = random.randint(1, 1000000)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)

# TODO: when session exists, load the previous messages and questions - this needs saving them to DB
# Save all questions and answers to DB for later analysis
# Add a feedback button to the UI & save the feedback to DB with the question and answer
# Add a token counter and warn the user when they are running out of tokens & ask to reset the session
# Test if multithreading works with sessions etc
# Improve CSS