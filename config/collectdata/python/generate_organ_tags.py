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

s = []
for r in ret["results"]["bindings"]:
        s.append(r)

organs = []
i = 0
for n in s:
    a = s[i]['x']['value'].replace("_", ":")
    a = a.partition('http://purl.obolibrary.org/obo/')[-1]
    b = s[i]['xLabel']['value'].replace(" ", "_")
    organs.append((a, b))
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