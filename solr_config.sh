#!/usr/bin/env bash
#
# Consolidated Solr Schema API script for fresh instance
# - Parse flags for host, port, and collection
# - Index CL_4023041 document
# - Define final field types (textEdge, textShingleEdge, nameExact, textStart)
# - Add autosuggest fields & copy-fields for label and synonym_* metadata
# - Clear all docs at the end
#
# Consult https://solr.apache.org/guide/8_11/schema-api.html for details

set -e

# Parse command-line options for host (-h), port (-p), collection (-c)
while getopts h:p:c: flag; do
  case "${flag}" in
    h) host=${OPTARG};;
    p) port=${OPTARG};;
    c) collection=${OPTARG};;
    *) echo "!!! Invalid flag. Only -h, -p, and -c are supported." && exit 1;;
  esac
done

# Validate required flags
[[ -z "$host"      ]] && echo "ERROR: host (-h) must be provided!"      && exit 1
[[ -z "$port"      ]] && echo "ERROR: port (-p) must be provided!"      && exit 1
[[ -z "$collection" ]] && echo "ERROR: collection (-c) must be provided!" && exit 1

BASE_URL="http://$host:$port/solr"
SCHEMA_URL="$BASE_URL/$collection/schema"

# 1) Index only the CL_4023041 document
echo "=== Indexing CL_4023041 document ==="
curl --location --request POST "$BASE_URL/$collection/update/json?commit=true" \
     --header 'Content-Type: application/json' \
     --data '[{"definition":["A glutamatergic neuron, with a soma found in the deeper portion of L5, that has long-range axonal .."],"facets_annotation":["Class","brain","Animal_cell"],"id":"http://purl.obolibrary.org/obo/CL_4023041","iri":["http://purl.obolibrary.org/obo/CL_4023041"],"label":["L5 extratelencephalic projecting glutamatergic cortical neuron"],"obo_id":["CL:4023041"],"short_form":["CL_4023041"],"synonym":["burst-firing layer 5 neuron","pyramidal tract (PT) neuron","L5 extratelencephalic projecting glutamatergic cortical neuron","thick-tufted layer 5 (TTL5) pyramidal neuron","L5b neuron","subcerebral projection (SCPN) neuron","Pyramidal tract-like (PT-l)"],"synonym_hasRelatedSynonym":["L5b neuron","subcerebral projection (SCPN) neuron"],"synonym_hasExactSynonym":["Pyramidal tract-like (PT-l)","burst-firing layer 5 neuron","thick-tufted layer 5 (TTL5) pyramidal neuron"],"synonym_hasNarrowSynonym":["pyramidal tract (PT) neuron"]}]'

echo
# 2) Define final field types
echo "=== Defining field types ==="

# 2.a) textEdge (with EnglishMinimalStemFilterFactory)
echo "- add-field-type textEdge"
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type":{
    "name":"textEdge",
    "class":"solr.TextField",
    "indexAnalyzer":{
      "tokenizer":{"class":"solr.StandardTokenizerFactory"},
      "filters":[
        {"class":"solr.WordDelimiterGraphFilterFactory","splitOnCaseChange":"0"},
        {"class":"solr.LowerCaseFilterFactory"},
        {"class":"solr.EdgeNGramFilterFactory","minGramSize":"2","maxGramSize":"35"}
      ]
    },
    "queryAnalyzer":{
      "tokenizer":{"class":"solr.WhitespaceTokenizerFactory"},
      "filters":[
        {"class":"solr.WordDelimiterGraphFilterFactory","splitOnCaseChange":"0"},
        {"class":"solr.EnglishMinimalStemFilterFactory"},
        {"class":"solr.LowerCaseFilterFactory"}
      ]
    }
  }
}' $SCHEMA_URL

# 2.b) textShingleEdge
echo "- add-field-type textShingleEdge"
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type":{
    "name":"textShingleEdge",
    "class":"solr.TextField",
    "indexAnalyzer":{
      "tokenizer":{"class":"solr.StandardTokenizerFactory"},
      "filters":[
        {"class":"solr.ShingleFilterFactory","maxShingleSize":"4","outputUnigrams":"false"},
        {"class":"solr.LowerCaseFilterFactory"},
        {"class":"solr.RemoveDuplicatesTokenFilterFactory"}
      ]
    },
    "queryAnalyzer":{
      "tokenizer":{"class":"solr.KeywordTokenizerFactory"},
      "filters":[
        {"class":"solr.LowerCaseFilterFactory"},
        {"class":"solr.RemoveDuplicatesTokenFilterFactory"}
      ]
    }
  }
}' $SCHEMA_URL

# 2.c) nameExact
echo "- add-field-type nameExact"
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type":{
    "name":"nameExact",
    "class":"solr.TextField",
    "indexAnalyzer":{"tokenizer":{"class":"solr.KeywordTokenizerFactory"},"filters":[{"class":"solr.LowerCaseFilterFactory"},{"class":"solr.RemoveDuplicatesTokenFilterFactory"}]},
    "queryAnalyzer":{"tokenizer":{"class":"solr.KeywordTokenizerFactory"},"filters":[{"class":"solr.LowerCaseFilterFactory"},{"class":"solr.RemoveDuplicatesTokenFilterFactory"}]}
  }
}' $SCHEMA_URL

# 2.d) textStart
echo "- add-field-type textStart"
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type":{
    "name":"textStart",
    "class":"solr.TextField",
    "indexAnalyzer":{
      "tokenizer":{"class":"solr.KeywordTokenizerFactory"},
      "filters":[{"class":"solr.LowerCaseFilterFactory"},{"class":"solr.RemoveDuplicatesTokenFilterFactory"},{"class":"solr.EdgeNGramFilterFactory","minGramSize":"3","maxGramSize":"35"}]
    },
    "queryAnalyzer":{"tokenizer":{"class":"solr.KeywordTokenizerFactory"},"filters":[{"class":"solr.LowerCaseFilterFactory"},{"class":"solr.RemoveDuplicatesTokenFilterFactory"}]}
  }
}' $SCHEMA_URL

echo
# 3) Add autosuggest fields & copy-field rules
echo "=== Adding autosuggest fields & copy-field rules ==="

autocomplete_single_val_fields=(label)
autocomplete_multi_val_fields=(synonym_hasExactSynonym synonym_hasNarrowSynonym synonym_hasRelatedSynonym)

for src in "${autocomplete_single_val_fields[@]}"; do
  for variant in e se ne ts; do
    declare -A type_map=( [e]=textEdge [se]=textShingleEdge [ne]=nameExact [ts]=textStart )
    echo "- add-field ${src}_autosuggest_${variant}"
    curl -X POST -H 'Content-type:application/json' --data-binary "{\"add-field\":{\"name\":\"${src}_autosuggest_${variant}\",\"type\":\"${type_map[$variant]}\",\"indexed\":true,\"stored\":true,\"multiValued\":false}}" $SCHEMA_URL
    echo "- add-copy-field ${src} → ${src}_autosuggest_${variant}"
    curl -X POST -H 'Content-type:application/json' --data-binary "{\"add-copy-field\":{\"source\":\"${src}\",\"dest\":\"${src}_autosuggest_${variant}\"}}" $SCHEMA_URL
  done
done

for src in "${autocomplete_multi_val_fields[@]}"; do
  for variant in e se ne ts; do
    declare -A type_map=( [e]=textEdge [se]=textShingleEdge [ne]=nameExact [ts]=textStart )
    echo "- add-field ${src}_autosuggest_${variant}"
    curl -X POST -H 'Content-type:application/json' --data-binary "{\"add-field\":{\"name\":\"${src}_autosuggest_${variant}\",\"type\":\"${type_map[$variant]}\",\"indexed\":true,\"stored\":true,\"multiValued\":true}}" $SCHEMA_URL
    echo "- add-copy-field ${src} → ${src}_autosuggest_${variant}"
    curl -X POST -H 'Content-type:application/json' --data-binary "{\"add-copy-field\":{\"source\":\"${src}\",\"dest\":\"${src}_autosuggest_${variant}\"}}" $SCHEMA_URL
  done
done

echo
# 4) Clear all docs at end
echo "=== Final Step: Clear all docs ==="
curl -X POST -H 'Content-Type: application/json' \
     "$BASE_URL/$collection/update?commit=true" \
     -d '{ "delete": {"query":"*:*"} }'

echo "Solr schema configuration complete."

