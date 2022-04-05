#!/usr/bin/env python3
# generate_organ_tags.py v1.0.0

# ACTION:
#  Generate list of IRIs and labels from UBERON organ_slim and output in JSON format to YAML file
#  Output will be used to filter and/or boost search results in Cell Annotation Platform (CAP)

# INSTRUCTIONS:
#  Organ IRIs and labels will be directed to a file named neo4j2owl-config.yaml by default
#  To direct output to a differnt file, execute by running:
#   python write_organ_tags.py -f file_name
#   Replace 'file_name' with name of YAML file

import argparse
import sys
import ruamel.yaml
from SPARQLWrapper import SPARQLWrapper, JSON

parser = argparse.ArgumentParser(description = 'set destination YAML file for query output')

parser.add_argument('-f', '--file', default = 'neo4j2owl-config.yaml', help = 'destination file')

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
# generate list of IRIs and organ labels
organs = []
for n in queryOutput:
    IRI = n['x']['value'].replace("_", ":")
    IRI = IRI.partition('http://purl.obolibrary.org/obo/')[-1]
    IRI = "cell and 'part of' some " + IRI
    label = n['xLabel']['value'].replace(" ", "_")
    organs.append((IRI, label))

# ramuel.yaml initialization and configuration
yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)

with open(file_name) as file:
    yaml_config = yaml.load(file)

# generate dictionary and populate with organ IRIs and labels
# organ_labels = {"neo_node_labelling": []}
for organ in organs:
    a = {'classes': organ[0], 'label': organ[1]}
    yaml_config['neo_node_labelling'].append(a)

# export populated dictionary to file
with open(file_name, 'w') as file:
    documents = yaml.dump(yaml_config, file)
