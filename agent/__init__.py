import os
import urllib

import json
from typing import List
from psycopg2 import extras

import psycopg2
from dotenv import load_dotenv
load_dotenv()
if 'DATABASE_URL' not in os.environ:
    raise Exception('DATABASE_URL environment variable not set')

DATABASE_URL = os.environ['DATABASE_URL']


def connect(db_url):
    url = urllib.parse.urlparse(db_url)
    return psycopg2.connect(
        host=url.hostname,
        database=url.path[1:],
        user=url.username,
        password=url.password
    )


class Article:
    def __init__(self, id, title, url, markdown, md_ada_002_embedding):
        self.id = id
        self.title = title
        self.url = url
        self.markdown = markdown
        self.md_ada_002_embedding = md_ada_002_embedding


def get_articles() -> List[Article]:
    with connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("SELECT id, title, url, markdown, md_ada_002_embedding FROM article WHERE deleted_at IS NULL")
            rows = cur.fetchall()

    articles = [Article(*row) for row in rows]
    return [article for article in articles if article.md_ada_002_embedding is not None]


ALL_ARTICLES = get_articles()
