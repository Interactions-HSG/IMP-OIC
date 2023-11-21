import networkx as nx

elist = [('hand', 'arm', 0.5), ('hand', 'person', 0.2), ('hand', 'finger', 0.6), ('glass', 'cup', 0.8),
         ('glass', 'cup', 0.8), ('person', 'woman', 0.8), ('person', 'man', 0.8), ('mouth', 'person', 0.4),
         ('mouth', 'woman', 0.4), ('mouth', 'man', 0.4), ('woman', 'girl', 0.9), ('man', 'boy', 0.9),
         ('boy', 'person', 0.9), ('girl', 'person', 0.9)]
SIMILAR_NAMES = nx.Graph()
SIMILAR_NAMES.add_weighted_edges_from(elist)

relation_to_text = {'above': 'was above', 'across': 'was across', 'against': 'was against', 'along': 'was along',
                    'and': 'and', 'at': 'was at', 'attached to': 'was attached to', 'behind': 'was behind',
                    'belonging to': 'belonged to', 'between': 'was between', 'carrying': 'carried',
                    'covered in': 'was covered in', 'covering': 'covered', 'eating': 'ate',
                    'flying in': 'flew in', 'for': 'was for', 'from': 'was from', 'growing on': 'grew on',
                    'hanging from': 'hung from', 'has': 'had', 'holding': 'held', 'in': 'was in',
                    'in front of': 'was in front of', 'laying on': 'laid on', 'looking at': 'looked at',
                    'lying on': 'was lying on', 'made of': 'was made of', 'mounted on': 'was mounted on',
                    'near': 'was near of', 'of': 'was a part of', 'on': 'was on', 'on back of': 'was on back of',
                    'over': 'was over', 'painted on': 'was painted on', 'parked on': 'was parked on',
                    'part of': 'was part of', 'playing': 'played', 'riding': 'rode', 'says': 'said',
                    'sitting on': 'sat on', 'standing on': 'stood on', 'to': 'was to', 'under': 'was under',
                    'using': 'used', 'walking in': 'walked in', 'walking on': 'walked on',
                    'watching': 'watched', 'wearing': 'wore', 'wears': 'wore', 'with': 'was with'}


def name_similarity(a, b):
    """
    Returns graph with name similarities for fuzzy matching
    """
    if a == b:
        #print("Name similarity =1")
        return 1
    else:
        if (a, b) in SIMILAR_NAMES.edges:
            #print("Name similarity !=1")
            return SIMILAR_NAMES[a][b]["weight"]
        else:
            #print("Name similarity =0")
            return 0


def convert_to_text(relation):
    if relation in relation_to_text.keys():
        return relation_to_text[relation]
    else:
        return f"was {relation}"
