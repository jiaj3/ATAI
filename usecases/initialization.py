import locale
import re

import editdistance
import rdflib
from rdflib.namespace import Namespace
from rdflib.term import URIRef, Literal
from transformers import pipeline

_ = locale.setlocale(locale.LC_ALL, '')
graph = rdflib.Graph()
graph.parse('./14_graph.nt', format='turtle')

WD = Namespace('http://www.wikidata.org/entity/')
WDT = Namespace('http://www.wikidata.org/prop/direct/')
SCHEMA = Namespace('http://schema.org/')
DDIS = Namespace('http://ddis.ch/atai/')
RDFS = rdflib.namespace.RDFS

entities = set(graph.subjects()) | {s for s in graph.objects() if isinstance(s, URIRef)}
predicates = set(graph.predicates())
literals = {s for s in graph.objects() if isinstance(s, Literal)}
with_type = set(graph.subjects(WDT['P31'], None))
with_super = set(graph.subjects(WDT['P279'], None))
types = set(graph.objects(None, WDT['P31']))
supers = set(graph.objects(None, WDT['P279']))
with_label = set(graph.subjects(RDFS.label, None))

ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')

nodes = {}
predicates_c = {}

for s, p, o in graph:
    # Extracting labels and node information
    if isinstance(s, URIRef):
        if (s, RDFS.label, None) in graph:
            nodes[s.toPython()] = graph.value(s, RDFS.label).toPython()
        else:
            nodes[s.toPython()] = re.sub('http://www.wikidata.org/entity/', "", s.toPython())

    if isinstance(p, URIRef):
        if (p, RDFS.label, None) in graph:
            predicates_c[p.toPython()] = graph.value(p, RDFS.label).toPython()


def extract_relation(question):
    relations = []

    return relations[0]


"""
1.extract entity and relation from the question
2.use entity/relation similarity to match the item in the graph(graph embedding)
3.match the entity and relation in the graph
4.construct query
5.answer generation
"""


def closed_question(question):
    # extract entity and relation from the question, entity using NER, and relation use
    entities_q = ner_pipeline(question, aggregation_strategy="simple")
    entity = ""
    for e in entities_q:
        entity += e['word'] + ' '
    entity = entity.strip()

    relation = 'director'

    # find the entity and relation in the graph
    tmp = 9999
    match_node = ""
    for key, value in nodes.items():
        if editdistance.eval(value, entity) < tmp:
            tmp = editdistance.eval(value, entity)
            match_node = key

    tmp = 9999
    match_pred = ""
    for key, value in predicates_c.items():
        if editdistance.eval(value, relation) < tmp:
            tmp = editdistance.eval(value, relation)
            match_pred = key

    sparql_query = """
    SELECT ?label
    WHERE {{
      {{
        <{0}> <{1}> ?item.
      }}
      UNION
      {{
        ?item <{1}> <{0}>.
      }}
      ?item rdfs:label ?label.
      FILTER(LANG(?label) = "en").
    }}
    LIMIT 1
    """.format(match_node, match_pred)

    results = graph.query(sparql_query)

    # Check if there's at least one result
    if results:
        label = results.bindings[0]["label"]
        return label
    else:
        # Handle the case when no result is found
        return "No result found"
