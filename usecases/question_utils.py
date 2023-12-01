

import locale

from transformers import pipeline
import spacy

from usecases.multimedia_utils import multimedia_question
from usecases.ner_utils import closed_question
from usecases.recommend_utils import recommend_question

_ = locale.setlocale(locale.LC_ALL, '')

nlp = spacy.load("../en_core_web_sm/en_core_web_sm-3.7.0")




def question(q):
    if "recommend" in q.lower():
        return recommend_question(q)
    elif "look" in q.lower() and "like" in q.lower():
        return multimedia_question(q)
    elif "picture" in q.lower():
        return multimedia_question(q)
    else:
        doc = nlp(q)
        for token in doc:
            if token.dep_ == "ROOT":
                if token.text == "watch":
                    return recommend_question(q)
        return closed_question(q)



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




