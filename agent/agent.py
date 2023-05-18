from os import environ
from agent.similar_articles import get_most_similar_articles_up_to_n_tokens, MODEL
import json
import openai

openai.api_key = environ.get('OPENAI_API_KEY')


PROMPT = '''You are a customer support agent at Wise, the money transfer company. Your job is to answer the customer by using only the info provided here. You will get a customer's question on one 
line, with the prefix "CUSTOMER: "
On the rest of the lines, you will get relevant information to answer the question. It starts with the prefix "CONTEXT: ".
Behave like you are the source of the information, while drawing answers only from the info provided. If your are unable to answer the question using the provided context, say 'I don't know'.
'''


def respond(question: str, previous_messages=[], previous_questions=[]):
    context, urls = get_relevant_context_to_anwer_questions(previous_questions, question)
    new_messages = build_new_messages(question, context, bool(previous_messages))
    llm_answer = fetch_llm_answer(new_messages, previous_messages)
    new_messages.append({"role": "assistant", "content": llm_answer})
    return llm_answer, urls, new_messages


def get_relevant_context_to_anwer_questions(previous_questions, question):
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


def fetch_llm_answer(new_messages, previous_messages):
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
    return list(filter(lambda m: not (m['role'] == 'system' and m['content'].startswith('CONTEXT: \n')), previous_messages))
