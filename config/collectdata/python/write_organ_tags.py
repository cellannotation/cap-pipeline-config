#!/usr/bin/env python3
# generate_organ_tags.py v1.0.0

# ACTION:
#  Generate list of organ cell DL queries and labels derived from UBERON organ_slim and send output to YAML file
#  Output will be used to filter and/or boost search results in Cell Annotation Platform (CAP)

# INSTRUCTIONS:
#  

import argparse
import sys
import ruamel.yaml
from SPARQLWrapper import SPARQLWrapper, JSON

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

sparql.setQuery("""
PREFIX inSubset: <http://www.geneontology.org/formats/oboInOwl#inSubset>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT  ?x ?xLabel
WHERE 
{
      ?x inSubset: <http://purl.obolibrary.org/obo/uberon/core#organ_slim> .
      ?x rdfs:label ?xLabel 
}
    """
                )

ret = sparql.queryAndConvert()

# uncomment to view query results
# for r in ret["results"]["bindings"]:
#    print(r)

queryOutput = []
for line in ret["results"]["bindings"]:
    queryOutput.append(line)

# generate list of organ cell DL queries and semantic labels
organs = []
for n in queryOutput:
    CURIE = n['x']['value'].replace("_", ":")
    CURIE = CURIE.partition('http://purl.obolibrary.org/obo/')[-1]
    dl_query = "cell and 'part of' some " + CURIE
    label = n['xLabel']['value'].replace(" ", "_")
    organs.append((dl_query, label))

# ramuel.yaml initialization and configuration
yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)

with open(file_name) as file:
    yaml_config = yaml.load(file)

# generate dictionary and populate with organ cell DL queries and sematic labels
# organ_labels = {"neo_node_labelling": []}
for organ in organs:
    a = {'classes': organ[0], 'label': organ[1]}
    yaml_config['neo_node_labelling'].append(a)

# export populated dictionary to file
with open(file_name, 'w') as file:
    documents = yaml.dump(yaml_config, file)
