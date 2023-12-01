import json

import editdistance

from usecases.graph_utils import graph, nodes, json_data
from usecases.ner_utils import ner_pipeline




def find_movie_image(json_data, target_id):
    if "nm" in target_id:
        for data in json_data:
            if target_id in data.get("cast"):
                img_path_or_url = data.get("img", "Image not found")
                return 'image:' + img_path_or_url[:-4]
    else:
        for data in json_data:
            if target_id in data.get("movie"):
                img_path_or_url = data.get("img", "Image not found")
                return 'image:' + img_path_or_url[:-4]
    return None

def match_entity(entity):
    tmp = 9999
    match_node = ""
    for key, value in nodes.items():
        if editdistance.eval(value, entity) < tmp:
            tmp = editdistance.eval(value, entity)
            match_node = key
    return match_node
def get_image(match_node):
    match_pred1 = "http://www.wikidata.org/prop/direct/P345"

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
    for row in result1.bindings:
        return row["item"].value


def multimedia_question(question):
    entity_q = ner_pipeline(question, aggregation_strategy="simple")
    match_node = match_entity(entity_q[0]['word'])
    image_list = get_image(match_node)
    if image_list == None:
        return "Image doesn't exist."


    images= find_movie_image(json_data, image_list)
    return images