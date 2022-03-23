#!/usr/bin/env python3
# generate_organ_tags.py v1.0.0

# ACTION: 
#  Generate list of IRIs and labels from UBERON organ_slim and output in JSON format
#  Output will be used to boost search results in Cell Annotation Platform (CAP) 

import sys
from ruamel.yaml import YAML
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper(
    "https://ubergraph.apps.renci.org/sparql"
)
sparql.setReturnFormat(JSON)


sparql.setQuery("""
prefix oio: <http://www.geneontology.org/formats/oboInOwl#>
prefix def: <http://purl.obolibrary.org/obo/IAO_0000115>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix inSubset: <http://www.geneontology.org/formats/oboInOwl#inSubset>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX overlaps: <http://purl.obolibrary.org/obo/RO_0002131>


SELECT  ?x ?xLabel
WHERE 
{
      ?x inSubset: <http://purl.obolibrary.org/obo/uberon/core#organ_slim> .
      ?x rdfs:label ?xLabel 
}
    """
)

ret = sparql.queryAndConvert()

# for r in ret["results"]["bindings"]:
#    print(r)

queryOutput = []
for line in ret["results"]["bindings"]:
        queryOutput.append(line)

organs = []
i = 0
for n in queryOutput:
    IRI = queryOutput[i]['x']['value'].replace("_", ":")
    IRI = IRI.partition('http://purl.obolibrary.org/obo/')[-1]
    label = queryOutput[i]['xLabel']['value'].replace(" ", "_")
    organs.append((IRI, label))
    i += 1

inp = """\
neo_node_labelling:
  classes: x
  label: y
"""

yaml = YAML()
code = yaml.load(inp)
i = 0
for organ in organs:
  code['neo_node_labelling']['classes'] = organs[i][0]
  code['neo_node_labelling']['label'] = organs[i][1]
  yaml.dump(code, sys.stdout)
  i += 1