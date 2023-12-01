import editdistance
from transformers import pipeline

import graph_utils
import embeddings_utils
import question_utils


ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')



def closed_question(question):
    # extract entity and relation from the question, entity using NER, and relation use
    entities_q = ner_pipeline(question, aggregation_strategy="simple")
    entity = ""
    temp_start = -1
    temp_end = 999
    if len(entities_q) > 1:
        for i, e in enumerate(entities_q):
            if e['entity_group'] == 'MISC':
                if temp_start == -1:
                    temp_start = e['start']
                temp_end = e['end']
        entity = question[temp_start: temp_end]
    else:
        for e in entities_q:
            entity += e['word'] + ' '
    entity = entity.strip()
    relation = question_utils.extract_relation(question)
    print(f"Entity: {entity}, Relation: {relation}")

    # find the entity and relation in the graph
    tmp = 9999
    match_node = ""
    for key, value in graph_utils.nodes.items():
        if editdistance.eval(value, entity) < tmp:
            tmp = editdistance.eval(value, entity)
            match_node = key

    tmp = 9999
    match_pred = ""
    for key, value in graph_utils.predicates_c.items():
        if editdistance.eval(value, relation) < tmp:
            tmp = editdistance.eval(value, relation)
            match_pred = key
    print(match_node, match_pred)

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
         LIMIT 1
         """.format(match_node, match_pred)
    results = graph_utils.graph.query(sparql_query)

    if results:
        if "label" in results.bindings[0]:
            label = embeddings_utils.check_embedding_question(match_node, match_pred, results.bindings[0]["label"])
            return f"The {relation} of {entity} is {label}."
        else:
            item = embeddings_utils.check_embedding_question(match_node, match_pred, results.bindings[0]["item"])
            return f"The {relation} of {entity} is {item} "
    else:
        # Handle the case when no result is found
        return embeddings_utils.check_embedding_question(match_node, match_pred, "No results")


def getrecommend(entity):
    # extract entity and relation from the question, entity using NER, and relation use

    tmp = 9999
    match_node = ""
    for key, value in graph_utils.nodes.items():
        if editdistance.eval(value, entity) < tmp:
            tmp = editdistance.eval(value, entity)
            match_node = key

    match_pred1 = "http://www.wikidata.org/prop/direct/P136"
    match_pred2 = "http://www.wikidata.org/prop/direct/P577"

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
             LIMIT 1
             """.format(match_node, match_pred1)
    result1 = graph_utils.graph.query(sparql_query)
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
                 LIMIT 1
                 """.format(match_node, match_pred2)
    result2 = graph_utils.graph.query(sparql_query)

    if result1:
        label = embeddings_utils.check_embedding_question(match_node, match_pred1, result1.bindings[0]["label"])
        """item = embeddings_utils.check_embedding_question(match_node, match_pred2, result2.bindings[0]["item"])"""
        return label
    else:
        label = embeddings_utils.check_embedding_question(match_node, match_pred1, "No results")
        """item = embeddings_utils.check_embedding_question(match_node, match_pred2, result2.bindings[0]["item"])"""
        return label


def get_genre_list(entity):

    # find the entity in the graph
    tmp = 9999
    match_node = ""
    for key, value in graph_utils.nodes.items():
        if editdistance.eval(value, entity) < tmp:
            tmp = editdistance.eval(value, entity)
            match_node = key

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
    result1 = graph_utils.graph.query(sparql_query)

    return [row["label"].value for row in result1.bindings]
