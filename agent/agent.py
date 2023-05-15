from os import environ
from agent.similar_articles import get_most_similar_articles_up_to_n_tokens, MODEL

import openai

openai.api_key = environ.get('OPENAI_API_KEY')


PROMPT = '''
You are a customer support agent at Wise, the money transfer company. Your job is to answer the customer by using only the info provided here. You will get a customer's question on one line,
with the prefix "CUSTOMER: "
On the rest of the lines, you will get relevant information to answer the question. It starts with the prefix "CONTEXT: ".
Behave like you are the source of the information, while drawing answers only from the info provided. If your are unable to answer the question using the provided context, say 'I don't know'.
'''


def respond(question: str, previous_messages=[], previous_questions=[]):
    if not previous_messages:
        new_messages = [{"role": "system", "content": PROMPT}, ]
    else:
        new_messages = []

    articles = get_most_similar_articles_up_to_n_tokens(' '.join(previous_questions) + ' ' + question)
    context = '\n\n'.join([article['content'] for article in articles.values()])
    new_messages.extend(
        [
            {"role": "user", "content": 'CUSTOMER:  \n' + question},
            {"role": "system", "content": 'CONTEXT: \n' + context}
        ]
    )
    urls = list(articles.keys())
    prompt_messages = list(filter(lambda m: not (m['role'] == 'system' and m['content'].startswith('CONTEXT: \n')), previous_messages))
    prompt_messages.extend(new_messages)
    chat = openai.ChatCompletion.create(
        model=MODEL,
        messages=prompt_messages
    )
    reply = chat.choices[0].message.content
    new_messages.append({"role": "assistant", "content": reply})

    return reply, urls, new_messages
