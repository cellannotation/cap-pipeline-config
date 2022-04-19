#!/usr/bin/env python3
# generate_organ_tags.py v1.0.0

# ACTION:
#  Generate list of organ cell DL queries and labels derived from UBERON organ_slim and send output to YAML file
#  Output will be used to filter and/or boost search results in Cell Annotation Platform (CAP)

import argparse
import ruamel.yaml
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import namedtuple


def run_query(query):
    sparql.setQuery(query)
    ret = sparql.queryAndConvert()
    output = []
    for line in ret["results"]["bindings"]:
        output.append(line)
    return output


def generate_organ_cells(output):
    organs = []
    for n in output:
        curie = n['x']['value'].replace("_", ":")
        curie = curie.partition('http://purl.obolibrary.org/obo/')[-1]
        dl_query = "CL:0000000 and BFO:0000050 some " + curie
        label = n['xLabel']['value'].replace(" ", "_")
        organs.append((dl_query, label))
    return organs


def update_neo_node_labelling(item_list):

    # Read the neo_node_labelling into a list of dict
    temp_list = yaml_config['neo_node_labelling']

    # Initialize list of Config namedtuple
    config_set = []
    Config = namedtuple('Config', 'classes label')
    for x in temp_list:
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
    temp_list = list()
    for i in converter:
        append = True
        for j in temp_list:
            if i.get('label') == j.get('label'):
                j.get('classes').extend(i.get('classes'))
                append = False
        if append:
            temp_list.append(i)

    # Write it back
    yaml_config['neo_node_labelling'] = converter


parser = argparse.ArgumentParser(description = 'set destination YAML file for query output')

parser.add_argument('-f', '--file', default = 'neo4j2owl-config.yaml', help = '''
    Use this option to indicate destination file for organ cell DL queries and semantic labels. By default, output
    is sent to a file named neo4j2owl-config.yaml.
    ''')

args = parser.parse_args()

file_name = args.file

sparql = SPARQLWrapper(
    "https://ubergraph.apps.renci.org/sparql"
)
sparql.setReturnFormat(JSON)

organ_query = """
PREFIX inSubset: <http://www.geneontology.org/formats/oboInOwl#inSubset>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT  ?x ?xLabel
WHERE 
{
      ?x inSubset: <http://purl.obolibrary.org/obo/uberon/core#organ_slim> .
      ?x rdfs:label ?xLabel 
}
    """

query_output = run_query(organ_query)

# generate list of organ cell DL queries and semantic labels
organ_list = generate_organ_cells(query_output)

# ramuel.yaml initialization and configuration
yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)

with open(file_name) as file:
    yaml_config = yaml.load(file)

update_neo_node_labelling(organ_list)

# export populated dictionary to file
with open(file_name, 'w') as file:
    documents = yaml.dump(yaml_config, file)
