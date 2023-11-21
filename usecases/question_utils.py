from recommend_utils import recommend_question
from ner_utils import closed_question


def question(q):
    if "recommend" in q.lower():
        return recommend_question(q)
    else:
        return closed_question(q)

