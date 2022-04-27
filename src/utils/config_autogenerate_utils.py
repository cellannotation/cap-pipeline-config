from SPARQLWrapper import SPARQLWrapper, JSON
from collections import namedtuple


def run_query(query):
    """Runs given sparql query using SPARQLWrapper and returns the query output

    Parameters:
    query (str): Sparql query to be run

    Returns:
    output (list): Query output
    """
    sparql = SPARQLWrapper(
        "https://ubergraph.apps.renci.org/sparql"
    )
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    ret = sparql.queryAndConvert()
    output = []
    for line in ret["results"]["bindings"]:
        output.append(line)
    return output


def update_neo_node_labelling(neo_node_labelling, item_list):
    """Updates given neo_node_labelling list with given item_list list, also removes duplicates. Returns updated list

    Parameters:
    neo_node_labelling (list): Semantic tag configurations in DL, a section in neo4j2owl-config.yaml
    item_list (list): Input list which contains new set of semantic tags and corresponding DLs

    Returns:
    output_list (list): Updated neo_node_labelling list
    """

    # Read the neo_node_labelling into a list of dict
    output_list = neo_node_labelling

    # Initialize list of Config namedtuple
    config_set = []
    Config = namedtuple('Config', 'classes label')
    for x in output_list:
        label = x['label']
        for classes in x['classes']:
            config = Config(classes, label)
            config_set.append(config)

    # Add given list items which contains classes and label pairs, generated automatically via SPARQL query
    for item in item_list:
        config = Config(item[0], item[1])
        config_set.append(config)

    # Remove duplicates
    config_set = set(config_set)

    # Convert list of namedtuple to list of dict
    converter = []
    for x in config_set:
        converter.append(x._asdict())

    # Change {'classes': 'UBERON:0010000', 'label': 'Multicellular_anatomical_structure'} to
    # {'classes': ['UBERON:0010000'], 'label': 'Multicellular_anatomical_structure'}
    for x in converter:
        x['classes'] = [x.get('classes')]

    # Merge classes based on labels
    output_list = list()
    for i in converter:
        append = True
        for j in output_list:
            if i.get('label') == j.get('label'):
                j.get('classes').extend(i.get('classes'))
                append = False
        if append:
            output_list.append(i)

    return output_list
