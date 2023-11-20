import locale
import re
import editdistance
from transformers import pipeline
import graph_utils
import embeddings_utils
import spacy

_ = locale.setlocale(locale.LC_ALL, '')

ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')

nlp = spacy.load("../en_core_web_sm/en_core_web_sm-3.7.0")


def extract_relation(question):
    relations = []
    doc = nlp(question)
    relation_mark = []
    if doc[0].dep_ == 'advmod':
        relation_mark = 1
    elif doc[0].dep_ == 'nsubj':
        relation_mark = 2
    if relation_mark == 1:
        return 'publication date'
    elif relation_mark == 2:
        return doc[0].head.text
    else:
        for token in doc:
            if token.dep_ == "ROOT":
                for child in token.children:
                    temp = child.text
                    for token_temp in reversed(list(doc)):
                        if token_temp.dep_ == 'compound' and token_temp.head.text == child.text:
                            temp = token_temp.text + ' ' + temp
                    relations.append(temp)
        return relations[1] if relations[1] else None


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
    relation = extract_relation(question)
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



