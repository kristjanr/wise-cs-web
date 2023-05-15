import numpy as np
import json

with open('embeddings/article_embeddings.npy', 'rb') as f:
    article_embeddings = np.load(f)


with open("scraped-data/index.json", "r") as f:
    index = json.load(f)
