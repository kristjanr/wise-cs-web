import random

from flask import Flask, render_template, request, session
import os
import secrets

from agent.agent import respond

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

message_history = {}
question_history = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/answer")
def answer():
    set_session_if_needed()
    question = request.args.get('question')
    if message_history.get(session['ID']) is None:

        reply, urls, new_messages = respond(question)

        message_history[session['ID']] = new_messages
        question_history[session['ID']] = [question]
        print("ID oli küll olemas, aga history_dictis polnud")
    else:
        previous_messages = message_history[session['ID']]
        previous_questions = question_history[session['ID']]

        reply, urls, new_messages = respond(question, previous_messages, previous_questions)

        message_history[session['ID']].extend(new_messages)
        question_history[session['ID']].append(question)

    print(new_messages)
    return dict(answer=reply, urls_used=urls)


def set_session_if_needed():
    if session.get('ID') is None:
        print("ID puudus")
        session['ID'] = random.randint(1, 1000000)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)
