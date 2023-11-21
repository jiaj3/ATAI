import random

import numpy as np
import pandas as pd
from transformers import pipeline
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import process
from collections import Counter
from ner_utils import getrecommend, get_genre_list

ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')
ml_ratings = pd.read_csv('../recommend_data/ratings.csv', usecols=['userId', 'movieId', 'rating'])
ml_matrix = ml_ratings.pivot(index='movieId', columns='userId', values='rating').fillna(0)
ml_csr = csr_matrix(ml_matrix.values)
movie_df = pd.read_csv('../recommend_data/movies.csv', usecols=['movieId', 'title'])
movie_dff = movie_df.drop(index=[0, 1]).reset_index(drop=True)
knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=17)
knn.fit(ml_csr[2:, :])


def search(entity):
    matches = movie_df.loc[movie_df['title'] == entity, 'movieId']

    if not matches.empty:
        movie_id = matches.iloc[0]
    else:
        best_match, score, idx = process.extractOne(entity, movie_df['title'])
        if score >= 80:
            movie_id = movie_df.loc[idx, 'movieId']
        else:
            movie_id = -1

    return movie_id


def helper(question):
    results = []
    entities_q = ner_pipeline(question, aggregation_strategy="simple")
    indices_all = []
    for e in entities_q:
        entity = e['word']
        id = search(entity)
        if id == -1:
            pass
        else:
            distances, indices = knn.kneighbors(ml_csr[id], n_neighbors=300)
            indices_all.append(indices)

    indices_all = np.hstack(indices_all).flatten()
    counter = Counter(indices_all)
    for i, count in counter.most_common(50):
        results.append(movie_dff['title'][i])
    return results


def recommend_question(question):
    entities_q = ner_pipeline(question, aggregation_strategy="simple")
    genre_list = []
    for e in entities_q:
        entity = e['word']
        genre = get_genre_list(entity)
        genre_list.extend(genre)

    counter = Counter(genre_list)
    finalgenre = [item for item, count in counter.items() if count > 1]

    candidates = helper(question)
    winners = []
    for c in candidates:
        if len(winners) > 2:
            break
        genre = get_genre_list(c)
        if set(genre).intersection(set(finalgenre)):
            winners.append(c)

    if winners:
        winners.append(candidates[0])

    sentences = [
        "You probably would also like " + ','.join(winners) + ".",
        "Why not also watch " + ','.join(winners) + "?"
    ]

    return random.choice(sentences)
