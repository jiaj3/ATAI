import random

import editdistance
import spacy
from transformers import pipeline
from collections import Counter

from usecases.graph_utils import graph, nodes
from usecases.ner_utils import ner_pipeline

instance_of_film = "http://www.wikidata.org/entity/Q11424"
match_instance = "http://www.wikidata.org/prop/direct/P31"
match_genre = "http://www.wikidata.org/prop/direct/P136"
match_distributed = "http://www.wikidata.org/prop/direct/P750"
match_AAWB = "http://www.wikidata.org/prop/direct/P1877"
match_series = "http://www.wikidata.org/prop/direct/P179"
match_director = "http://www.wikidata.org/prop/direct/P57"
match_cast = "http://www.wikidata.org/prop/direct/P161"
match_date = "http://www.wikidata.org/prop/direct/P577"

nlp = spacy.load("../en_core_web_sm/en_core_web_sm-3.7.0")

import random

import editdistance
from collections import Counter

'''
2 ciurcumstances:
1. given a list of movies: check genre, after a work by, part of the series, distributed by
2. given human name

else if entity == none, try extracting genre!

exclude original names!

'''


def check_instance(node):
    match_instance = "http://www.wikidata.org/prop/direct/P31"
    sparql_query = """
            SELECT ?item ?label
            WHERE {{
              {{
                <{0}> <{1}> ?item.
              }}
              UNION
              {{
                ?item <{1}> <{0}>.
              }}
              OPTIONAL {{
                ?item rdfs:label ?label.
                FILTER(LANG(?label) = "en").
              }}
            }}
            """.format(node, match_instance)
    result1 = graph.query(sparql_query)
    result = []
    for row in result1.bindings:
        result.append(row["label"].value if "label" in row else "Label not available")
    return result


def try_get_genre(sentence):
    doc = nlp(sentence)
    entity = ""
    for token in doc:
        if "film" in token.head.text or "movie" in token.head.text:
            if token.dep_ == 'compound':
                entity = token.text + ' film'
    if entity == None:
        return
    tmp = 9999
    match_node = ""
    for key, value in nodes.items():
        if editdistance.eval(value, entity) < tmp:
            tmp = editdistance.eval(value, entity)
            match_node = key
    return match_node


def match_entity_movie(entity):
    tmp = 9999
    match_node = ""
    for key, value in nodes.items():
        if editdistance.eval(value, entity) < tmp:
            instance = check_instance(key)
            if "film" in instance[0]:
                tmp = editdistance.eval(value, entity)
                match_node = key
    return match_node


def match_entity_person(entity):
    tmp = 9999
    match_node = ""
    for key, value in nodes.items():
        if editdistance.eval(value, entity) < tmp:
            tmp = editdistance.eval(value, entity)
            match_node = key
    return match_node


def get_genre(match_node):
    match_pred1 = "http://www.wikidata.org/prop/direct/P136"

    sparql_query = """
            SELECT ?item ?label
            WHERE {{
              {{
                <{0}> <{1}> ?item.
              }}
              UNION
              {{
                ?item <{1}> <{0}>.
              }}
              OPTIONAL {{
                ?item rdfs:label ?label.
                FILTER(LANG(?label) = "en").
              }}
            }}
            """.format(match_node, match_pred1)
    result1 = graph.query(sparql_query)
    result = []
    for row in result1.bindings:
        result.append(row["label"].value if "label" in row else "Label not available")
    return result1.bindings


def get_distributed(match_node):
    match_pred1 = "http://www.wikidata.org/prop/direct/P750"

    sparql_query = """
            SELECT ?item ?label
            WHERE {{
              {{
                <{0}> <{1}> ?item.
              }}
              UNION
              {{
                ?item <{1}> <{0}>.
              }}
              OPTIONAL {{
                ?item rdfs:label ?label.
                FILTER(LANG(?label) = "en").
              }}
            }}
            """.format(match_node, match_pred1)
    result1 = graph.query(sparql_query)
    result = []
    for row in result1.bindings:
        result.append(row["label"].value if "label" in row else "Label not available")
    return result1.bindings


def get_AAWB(match_node):
    match_pred1 = "http://www.wikidata.org/prop/direct/P1877"

    sparql_query = """
            SELECT ?item ?label
            WHERE {{
              {{
                <{0}> <{1}> ?item.
              }}
              UNION
              {{
                ?item <{1}> <{0}>.
              }}
              OPTIONAL {{
                ?item rdfs:label ?label.
                FILTER(LANG(?label) = "en").
              }}
            }}
            """.format(match_node, match_pred1)
    result1 = graph.query(sparql_query)
    result = []
    for row in result1.bindings:
        result.append(row["label"].value if "label" in row else "Label not available")
    return result1.bindings


def get_series(match_node):
    match_pred1 = "http://www.wikidata.org/prop/direct/P179"

    sparql_query = """
            SELECT ?item ?label
            WHERE {{
              {{
                <{0}> <{1}> ?item.
              }}
              UNION
              {{
                ?item <{1}> <{0}>.
              }}
              OPTIONAL {{
                ?item rdfs:label ?label.
                FILTER(LANG(?label) = "en").
              }}
            }}
            """.format(match_node, match_pred1)
    result1 = graph.query(sparql_query)
    result = []
    for row in result1.bindings:
        result.append(row["label"].value if "label" in row else "Label not available")
    return result1.bindings


def series(sorted_series_list):
    sparql_query = f"""
    SELECT ?film ?filmLabel
    WHERE {{
      ?film <{match_series}> <{sorted_series_list[0][0]['item']}>.
    }}"""

    result = graph.query(sparql_query)
    returnlist = []
    for row in result.bindings:
        returnlist.append(row['film'])
    return returnlist


def AAWB(list):
    sparql_query = f"""
    SELECT ?film ?filmLabel
    WHERE {{
      ?film <{match_AAWB}> <{list[0][0]['item']}>.
    }}"""

    result = graph.query(sparql_query)
    returnlist = []
    for row in result.bindings:
        returnlist.append(row['film'])
    return returnlist


def distributed(distributedlist, genrelist):
    sparql_query = f"""
    SELECT ?film ?filmLabel
    WHERE {{
      ?film <{match_distributed}> <{distributedlist[0][0]['item']}>;
            <{match_genre}> <{genrelist[0][0]['item']}>.
    }}"""

    result = graph.query(sparql_query)
    returnlist = []
    for row in result.bindings:
        returnlist.append(row['film'])
    return returnlist


def genre(genrelist):
    sparql_query = f"""
    SELECT ?film ?filmLabel
    WHERE {{
      ?film <{match_genre}> <{genrelist[0][0]['item']}>.
    }}"""

    result = graph.query(sparql_query)
    returnlist = []
    for row in result.bindings:
        returnlist.append(row['film'])
    return returnlist


def person(match_person, genrelist):
    if genrelist == []:
        sparql_query = f"""
            SELECT ?film ?filmLabel
            WHERE {{
              ?film <{match_director}> <{match_person}>.
            }}"""

        result = graph.query(sparql_query)
        returnlist = []
        for row in result.bindings:
            returnlist.append(row['film'])
        if len(returnlist) < 4:
            sparql_query = f"""
                        SELECT ?film ?filmLabel
                        WHERE {{
                          ?film <{match_cast}> <{match_person}>.
                        }}"""

            result = graph.query(sparql_query)
            for row in result.bindings:
                returnlist.append(row['film'])
    else:
        sparql_query = f"""
            SELECT ?film ?filmLabel
            WHERE {{
              ?film <{match_director}> <{match_person}>;
                    <{match_genre}> <{genrelist[0][0]['item']}>.
            }}"""

        result = graph.query(sparql_query)
        returnlist = []
        for row in result.bindings:
            returnlist.append(row['film'])
        if len(returnlist) < 4:
            sparql_query = f"""
                        SELECT ?film ?filmLabel
                        WHERE {{
                          ?film <{match_cast}> <{match_person}>;
                                <{match_genre}> <{genrelist[0][0]['item']}>.
                        }}"""

            result = graph.query(sparql_query)
            for row in result.bindings:
                returnlist.append(row['film'])
        if len(returnlist) < 4:
            sparql_query = f"""
            SELECT ?film ?filmLabel
            WHERE {{
              ?film <{match_director}> <{match_person}>.
            }}"""

        result = graph.query(sparql_query)
        returnlist = []
        for row in result.bindings:
            returnlist.append(row['film'])
        if len(returnlist) < 4:
            sparql_query = f"""
                        SELECT ?film ?filmLabel
                        WHERE {{
                          ?film <{match_cast}> <{match_person}>.
                        }}"""

            result = graph.query(sparql_query)
            for row in result.bindings:
                returnlist.append(row['film'])
    return returnlist


def recommend_question(question):
    entity_q = ner_pipeline(question, aggregation_strategy="simple")
    entity = []
    people = []
    for e in entity_q:
        if e['entity_group'] == "MISC":
            entity.append(e['word'])
        else:
            people.append(e['word'])

    match_node = []
    match_person = ""
    for e in entity:
        match_node.append(match_entity_movie(e))
    for e in people:
        match_person = match_entity_person(e)
    genre_list = []
    distributed_list = []
    AAWB_list = []
    series_list = []

    for node in match_node:
        genre_list.extend(get_genre(node))
        distributed_list.extend(get_distributed(node))
        AAWB_list.extend(get_AAWB(node))
        series_list.extend(get_series(node))

    counter_genre = Counter(genre_list)
    counter_distributed = Counter(distributed_list)
    counter_AAWB = Counter(AAWB_list)
    counter_series = Counter(series_list)

    genre_list = counter_genre.most_common(3)
    distributed_list = counter_distributed.most_common(3)
    AAWB_list = counter_AAWB.most_common(1)
    series_list = counter_series.most_common(1)

    def get_qid(item):
        return int(item[0]['item'].split('/')[-1][1:])

    sorted_genre_list = sorted(genre_list, key=get_qid, reverse=True)
    sorted_distributed_list = sorted(distributed_list, key=get_qid, reverse=True)
    sorted_AAWB_list = sorted(AAWB_list, key=get_qid, reverse=True)
    sorted_series_list = sorted(series_list, key=get_qid, reverse=True)

    result = []

    if match_person != "":
        templist = person(match_person, sorted_genre_list)
        for temp in templist:
            if temp not in match_node:
                result.append(temp)
    else:
        if sorted_series_list != []:
            templist = series(sorted_series_list)
            for temp in templist:
                if temp not in match_node:
                    result.append(temp)
        if len(result) < 4 and sorted_AAWB_list != []:
            templist = AAWB(sorted_AAWB_list)
            for temp in templist:
                if temp not in match_node:
                    result.append(temp)

        if len(result) < 4 and sorted_distributed_list != []:
            templist = distributed(sorted_distributed_list, genre_list)
            for temp in templist:
                if temp not in match_node:
                    result.append(temp)

        if len(result) < 4 and sorted_genre_list != []:
            templist = genre(genre_list)
            for temp in templist:
                if temp not in match_node:
                    result.append(temp)
    winners = []
    match_name = []
    for e in match_node:
        name, date = get_film_info(e)
        if name == ".":
            pass
        else:
            match_name.append(name)

    count = 3
    for film in result:
        name, date = get_film_info(film)
        if name == ".":
            pass
        elif name not in match_name:
            winners.append(name + "(" + date + ")")
            count -= 1
        if count == 0:
            break

    sentences = [
        "You probably would also like " + ','.join(winners) + ".",
        "Why not also watch " + ','.join(winners) + "?"
    ]

    return random.choice(sentences)


def get_film_info(node):
    sparql_query = f"""
    SELECT ?publicationDate ?label
    WHERE {{
      <{node}> <{match_date}> ?publicationDate.
      <{node}> rdfs:label ?label.
      FILTER(LANG(?label) = "en").
    }}
    """

    result = graph.query(sparql_query)
    for row in result.bindings:
        return row['label'], row['publicationDate'][:4]
    return ".", "."


