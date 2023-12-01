import json
import locale
import rdflib
from rdflib.namespace import Namespace
from rdflib.term import URIRef, Literal
import re



def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

json_file_path = '../images.json'
json_data = load_json_file(json_file_path)


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