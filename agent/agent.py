import time
from os import environ

import tiktoken

from agent.similar_articles import get_most_similar_articles_up_to_n_tokens, MODEL
import json
import openai
import logging

openai.api_key = environ.get('OPENAI_API_KEY')

PROMPT = '''You are a customer support agent at Wise, the money transfer company. Your job is to answer the customer by using only the info provided here. You will get a customer's question on one 
line, with the prefix "CUSTOMER: "
On the rest of the lines, you will get relevant information to answer the question. It starts with the prefix "CONTEXT: ".
Behave like you are the source of the information, while drawing answers only from the info provided. If your are unable to answer the question using the provided context, say 'I don't know'.
Do not ask any account or transaction details, except those which would help finding the answer from the context provided.
'''


def respond(question: str, previous_messages=[], previous_questions=[]) -> (str, list, list):
    start_time_context = time.time()
    context, urls = get_relevant_context_to_answer_questions(previous_questions, question)
    end_time_context = time.time()
    context_time = end_time_context - start_time_context

    new_messages = build_new_messages(question, context, bool(previous_messages))

    start_time_llm = time.time()
    llm_answer = fetch_llm_answer(new_messages, previous_messages)
    end_time_llm = time.time()
    llm_time = end_time_llm - start_time_llm

    new_messages.append({"role": "assistant", "content": llm_answer})

    logging.info(f'Context generation time: {context_time} seconds')
    logging.info(f'LLM answer generation time: {llm_time} seconds')

    return llm_answer, urls, new_messages


def get_relevant_context_to_answer_questions(previous_questions, question):
    articles = get_most_similar_articles_up_to_n_tokens(f"{' '.join(previous_questions)} {question}")
    context = '\n\n'.join([article['content'] for article in articles.values()])
    urls = list(articles.keys())
    return context, urls


def build_new_messages(question, context, previous_messages_exist):
    if not previous_messages_exist:
        new_messages = [{"role": "system", "content": PROMPT}, ]
    else:
        new_messages = []
    new_messages.extend(
        [
            {"role": "user", "content": 'CUSTOMER:  \n' + question},
            {"role": "system", "content": 'CONTEXT: \n' + context}
        ]
    )
    return new_messages


MODEL = "gpt-3.5-turbo"
tokenizer = tiktoken.encoding_for_model(MODEL)


def fetch_llm_answer(new_messages, previous_messages):
    previous_messages_tokens = []
    for message in previous_messages:
        try:
            previous_messages_tokens.append(len(tokenizer.encode(message['content'])))
        except TypeError:
            logging.error(f'Could not encode message: {message}')
    if sum(previous_messages_tokens) > 1500:
        logging.info(f'Previous messages too long, removing first two messages')
        previous_messages = []
    # prompt_messages = remove_big_messages(previous_messages)
    prompt_messages = previous_messages
    prompt_messages.extend(new_messages)
    print(f'First 200 chars of messages sent to LLM: {[json.dumps(m)[:200] for m in prompt_messages]}')
    chat = openai.ChatCompletion.create(
        model=MODEL,
        messages=prompt_messages
    )
    reply = chat.choices[0].message.content
    return reply


def remove_big_messages(previous_messages):
    return list(
        filter(lambda m: not (m['role'] == 'system' and m['content'].startswith('CONTEXT: \n')), previous_messages))
