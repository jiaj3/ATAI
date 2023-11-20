from recommend_utils import recommend_question


def question(q):
    if "recommend" in q.lower():
        return recommend_question(q)
    else:
        return

