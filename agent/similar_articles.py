from typing import List, Tuple

import openai

import numpy as np
import tiktoken

from os import environ

from agent import Article, ALL_ARTICLES

openai.api_key = environ.get('OPENAI_API_KEY')

EMBEDDING_MODEL = "text-embedding-ada-002"


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(
        model=model,
        input=text
    )
    return result["data"][0]["embedding"]


# 	$0.002 / 1K tokens
# 4,096 tokens = $0.008192

def vector_similarity(x: list[float], y: list[float]) -> np.array:
    """
    Returns the similarity between two vectors.

    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


def get_similar_articles(question: str) -> list[tuple[float, Article]]:
    print(f'Looking similar articles for question: {question}')
    question_embedding = get_embedding(question)
    article_similarities = []
    for article in ALL_ARTICLES:
        similarity = vector_similarity(question_embedding, article.md_ada_002_embedding)
        article_similarities.append((similarity, article))

    return sorted(article_similarities, reverse=True)


MODEL = "gpt-4"
tokenizer = tiktoken.encoding_for_model(MODEL)


def get_most_similar_articles_up_to_n_tokens(question: str, max_tokens=2000) -> dict[str, dict]:
    articles = {
        article.url: dict(content=article.markdown, tokens=len(tokenizer.encode(article.markdown))) for
        similarity, article in get_similar_articles(question)}

    token_count = 0
    filtered_articles = {}
    for url, article in articles.items():
        if token_count + article['tokens'] < max_tokens:
            token_count += article['tokens']
            filtered_articles[url] = article
        else:
            break
    return filtered_articles
