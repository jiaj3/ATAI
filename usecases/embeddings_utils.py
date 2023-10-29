import csv
import numpy as np
import os
import rdflib
import pandas as pd
from sklearn.metrics import pairwise_distances
import graph_utils

# define some prefixes
WD = rdflib.Namespace('http://www.wikidata.org/entity/')
WDT = rdflib.Namespace('http://www.wikidata.org/prop/direct/')
DDIS = rdflib.Namespace('http://ddis.ch/atai/')
RDFS = rdflib.namespace.RDFS
SCHEMA = rdflib.Namespace('http://schema.org/')

# load the embeddings
entity_emb = np.load('../ddis-graph-embeddings/entity_embeds.npy')
relation_emb = np.load('../ddis-graph-embeddings/relation_embeds.npy')

# load the dictionaries
with open('../ddis-graph-embeddings/entity_ids.del', 'r') as ifile:
    ent2id = {rdflib.term.URIRef(ent): int(idx) for idx, ent in csv.reader(ifile, delimiter='\t')}
    id2ent = {v: k for k, v in ent2id.items()}
with open('../ddis-graph-embeddings/relation_ids.del', 'r') as ifile:
    rel2id = {rdflib.term.URIRef(rel): int(idx) for idx, rel in csv.reader(ifile, delimiter='\t')}
    id2rel = {v: k for k, v in rel2id.items()}

ent2lbl = {ent: str(lbl) for ent, lbl in graph_utils.graph.subject_objects(RDFS.label)}
lbl2ent = {lbl: ent for ent, lbl in ent2lbl.items()}

def check_embedding_question(node, predicate, result):
    entity_id = node.split('/')[-1]
    relation_id = predicate.split('/')[-1]

    try:
        head = entity_emb[ent2id[WD[entity_id]]]
        pred = relation_emb[rel2id[WDT[relation_id]]]
    except KeyError as e:
        return result

    # add vectors according to TransE scoring function.
    lhs = head + pred
    # compute distance to *any* entity
    dist = pairwise_distances(lhs.reshape(1, -1), entity_emb).reshape(-1)
    # find most plausible entities
    most_likely = dist.argsort()
    # compute ranks of entities
    ranks = dist.argsort().argsort()
    in_top_six = False
    for rank, idx in enumerate(most_likely[:6]):
        if result.strip() == ent2lbl[id2ent[idx]].strip():
            in_top_six = True
    if in_top_six == True:
        return result
    else:
        return ent2lbl[id2ent[most_likely[0]]]

