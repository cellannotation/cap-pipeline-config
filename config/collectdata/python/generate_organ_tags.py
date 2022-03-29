#!/usr/bin/env python3
# generate_organ_tags.py v1.0.0

# ACTION:
#  Generate list of IRIs and labels from UBERON organ_slim and output in JSON format
#  Output will be used to filter and/or boost search results in Cell Annotation Platform (CAP)

import sys
import ruamel.yaml
from SPARQLWrapper import SPARQLWrapper, JSON

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
    label = n['xLabel']['value'].replace(" ", "_")
    organs.append((IRI, label))

# ramuel.yaml initialization and configuration
yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)

with open('neo4j2owl-config.yaml') as file:
    yaml_config = yaml.load(file)

# generate dictionary and populate with organ IRIs and labels
# organ_labels = {"neo_node_labelling": []}
for organ in organs:
#   print(organ)
    a = {'classes': organ[0], 'label': organ[1]}
    yaml_config['neo_node_labelling'].append(a)

# export populated dictionary to file
# ? can neo4j2owl-config.yaml point to this file?
with open('neo4j2owl-config.yaml', 'w') as file:
    documents = yaml.dump(yaml_config, file)