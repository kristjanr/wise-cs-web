import openai

from backend.agent import index, article_embeddings
import numpy as np
import tiktoken

from os import environ

openai.api_key = environ.get('OPENAI_API_KEY')

EMBEDDING_MODEL = "text-embedding-ada-002"


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(
        model=model,
        input=text
    )
    return result["data"][0]["embedding"]


def return_content(article_id):
    counter = 0
    for section in index:
        for subsection in section["subsections"]:
            for article in subsection["articles"]:
                if counter != article_id:
                    counter += 1
                    continue
                with open(article['folder_path'] + '/content.md', 'r') as f:
                    article_md = f.read()
                items = [section["title"], section["heading"], article_md]
                content = '\n\n'.join(items)
                return content, 'https://wise.com' + article['link']


# 	$0.002 / 1K tokens
# 4,096 tokens = $0.008192

def vector_similarity(x: list[float], y: list[float]) -> np.array:
    """
    Returns the similarity between two vectors.

    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))


def get_similar_articles(question: str) -> list[tuple[float, int]]:
    print(f'Looking similar articles for question: {question}')
    question_embedding = get_embedding(question)
    article_similarities = []
    for article_nr, article_embedding in enumerate(article_embeddings):
        similarity = vector_similarity(question_embedding, article_embedding)
        article_similarities.append((similarity, article_nr))

    return sorted(article_similarities, reverse=True)


MODEL = "gpt-3.5-turbo"
tokenizer = tiktoken.encoding_for_model(MODEL)


def get_most_similar_articles_up_to_n_tokens(question: str, max_tokens=1000) -> dict[str, dict]:
    article_similarities = get_similar_articles(question)
    articles = [return_content(article_similarities[i][1]) for i in range(5)]
    top_five_similar_articles = {url: dict(content=md, tokens=len(tokenizer.encode(md))) for md, url in articles}

    token_count = 0
    filtered_articles = {}
    for url, article in top_five_similar_articles.items():
        if token_count + article['tokens'] < max_tokens:
            token_count += article['tokens']
            filtered_articles[url] = article
        else:
            break
    return filtered_articles
