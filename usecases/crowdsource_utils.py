from ner_utils import extract_entity_relation, get_label
import pandas as pd

file_path = '../crowd_data/crowd_data.tsv'
crowdsource = pd.read_csv(file_path, sep='\t')

crowdsource['LifetimeApprovalRate'] = crowdsource['LifetimeApprovalRate'].str.rstrip('%').astype(float)

crowdsource_not_malicious = crowdsource[(crowdsource['WorkTimeInSeconds'] > 10) &
                                        (crowdsource['LifetimeApprovalRate'] > 50)]
crowdsource_not_malicious.loc[:, 'AnswerLabel'] = crowdsource_not_malicious['AnswerLabel'].replace(
    {'INCORRECT': 'reject', 'CORRECT': 'support'})

batches = crowdsource_not_malicious.groupby('HITTypeId')
fleiss_kappa_values = {'7QT': 0.236, '8QT': 0.040, '9QT': 0.263}


def checkIfCrowdsource(question):
    print(question)
    entity, match_node, match_pred, relation = extract_entity_relation(question)
    print([entity, match_node, match_pred, relation])

    filtered_data = crowdsource_not_malicious[
        (crowdsource['Input1ID'] == 'wd:' + match_node.split('/')[-1]) &
        (crowdsource['Input2ID'] == 'wdt:' + match_pred.split('/')[-1])
        ]

    print(filtered_data)
    if filtered_data.empty:
        return False
    else:
        return True


def crowdsource_question(question):
    entity, match_node, match_pred, relation = extract_entity_relation(question)

    # filter out WorkTimeInSeconds less than 5s and worker's LifetimeApprovalRate less than 50%
    filtered_data = crowdsource_not_malicious[
        (crowdsource['Input1ID'] == 'wd:' + match_node.split('/')[-1]) &
        (crowdsource['Input2ID'] == 'wdt:' + match_pred.split('/')[-1])
        ]

    fleiss_kappa_0 = fleiss_kappa_values[filtered_data['HITTypeId'].values[0]]

    label_counts = filtered_data['AnswerLabel'].value_counts()
    sorted_label_counts = label_counts.sort_values(ascending=False)
    more_votes = f'{sorted_label_counts.iloc[0]} {sorted_label_counts.index[0]}'
    if len(sorted_label_counts) > 1:
        less_votes = f'{sorted_label_counts.iloc[1]} {sorted_label_counts.index[1]}'
    elif sorted_label_counts.iloc[0] == 'support':
        less_votes = f'0 reject'
    else:
        less_votes = f'0 support'

    crowd_object = filtered_data['Input3ID'].values[0]
    if 'wd' in crowd_object:
        crowd_object = get_label(crowd_object)

    if sorted_label_counts.index[0] == 'reject':
        most_common_fix_position = filtered_data['FixPosition'].value_counts().idxmax()
        most_common_fix_value = filtered_data['FixValue'].value_counts().idxmax()
        if most_common_fix_position == 'Subject':
            if 'wd:Q' in most_common_fix_value:
                entity = get_label(most_common_fix_value)
            elif 'Q' in most_common_fix_value:
                entity = get_label('wd:'+most_common_fix_value)
            else:
                entity = most_common_fix_value
        elif most_common_fix_position == 'Object':
            if 'wd:Q' in most_common_fix_value:
                crowd_object = get_label(most_common_fix_value)
            elif 'Q' in most_common_fix_value:
                crowd_object = get_label('wd:'+most_common_fix_value)
            else:
                crowd_object = most_common_fix_value
        else:
            if 'wdt:P' in most_common_fix_value:
                relation = get_label(most_common_fix_value)
            elif 'P' in most_common_fix_value:
                relation = get_label('wdt:'+most_common_fix_value)
            else:
                relation = most_common_fix_value

    answer = (f"The {relation} of {entity} is {crowd_object}.\n"
              f"[Crowd, inter-rater agreement {fleiss_kappa_0}, The answer distribution for this specific task was "
              f"{more_votes} votes, {less_votes} votes] ")

    return answer
