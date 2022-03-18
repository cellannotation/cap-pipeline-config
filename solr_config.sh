#!/bin/bash
#
# This script updates ontology schema with ngram based new search fields. These new text fields has naming: *_autosuggest_e
# and *_autosuggest_wse, and enable partial matching capability. To run this script, your solr should be up and running
# and the latest dump file, solr.json, is uploaded.
#
# Important: After the schema change, reindexing is required. For this purpose, you can simply re-upload the dump data
# to the ontology collection.
#
# Usage:
# bash solr_post_config.sh -h localhost -p 8993

set -e

core_name=ontology
autocomplete_single_val_fields=(label unique_facets)
autocomplete_multi_val_fields=(synonym facets_annotation)

autocomplete_fields=("${autocomplete_single_val_fields[@]}" "${autocomplete_multi_val_fields[@]}")

while getopts h:p: flag
do
    case "${flag}" in
        h) host=${OPTARG};;
        p) port=${OPTARG};;
        *) echo "!!! Invalid flag. Only -h and -p flags are supported."
    esac
done

echo "Updating $core_name in server $host:$port"

echo "Adding textEdge field type"
curl -X POST -H 'Content-type:application/json' --data-binary "{
  \"add-field-type\":{
    \"name\":\"textEdge\",
    \"class\":\"solr.TextField\",
    \"indexAnalyzer\":{
      \"tokenizer\":{
         \"class\":\"solr.PatternTokenizerFactory\",
         \"pattern\":\"______\" },
       \"filters\":[{\"class\":\"solr.LowerCaseFilterFactory\" },
                   {\"class\":\"solr.RemoveDuplicatesTokenFilterFactory\" },
                   {\"class\":\"solr.EdgeNGramFilterFactory\",
                   \"minGramSize\":\"1\",
                   \"maxGramSize\":\"35\"}]
    },
    \"queryAnalyzer\":{
      \"tokenizer\":{
         \"class\":\"solr.PatternTokenizerFactory\",
         \"pattern\":\"______\" },
       \"filters\":[{\"class\":\"solr.LowerCaseFilterFactory\" },
                   {\"class\":\"solr.RemoveDuplicatesTokenFilterFactory\" }]
    }
  }
}" http://$host:$port/solr/$core_name/schema --show-error --fail

echo "Adding textWhitespaceEdge field type"
curl -X POST -H 'Content-type:application/json' --data-binary "{
  \"add-field-type\":{
    \"name\":\"textWhitespaceEdge\",
    \"class\":\"solr.TextField\",
    \"indexAnalyzer\":{
      \"tokenizer\":{
         \"class\":\"solr.WhitespaceTokenizerFactory\" },
       \"filters\":[{\"class\":\"solr.LowerCaseFilterFactory\" },
                   {\"class\":\"solr.RemoveDuplicatesTokenFilterFactory\" },
                   {\"class\":\"solr.EdgeNGramFilterFactory\",
                   \"minGramSize\":\"1\",
                   \"maxGramSize\":\"35\"}]
    },
    \"queryAnalyzer\":{
      \"tokenizer\":{
         \"class\":\"solr.WhitespaceTokenizerFactory\" },
       \"filters\":[{\"class\":\"solr.LowerCaseFilterFactory\" },
                   {\"class\":\"solr.RemoveDuplicatesTokenFilterFactory\" }]
    }
  }
}" http://$host:$port/solr/$core_name/schema --show-error --fail

echo "Adding auto complete single value fields: ${autocomplete_single_val_fields[*]}"
for field in "${autocomplete_single_val_fields[@]}"; do

  echo "Adding auto complete field e: ${field}"
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-field\":{
       \"name\":\"${field}_autosuggest_e\",
       \"type\":\"textEdge\",
       \"indexed\":true,
       \"stored\":true,
       \"multiValued\":false
     }
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

  echo "Adding auto complete field wse: ${field}"
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-field\":{
       \"name\":\"${field}_autosuggest_wse\",
       \"type\":\"textWhitespaceEdge\",
       \"indexed\":true,
       \"stored\":true,
       \"multiValued\":false
     }
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

# end for
done

echo "Adding auto complete multi value fields: ${autocomplete_multi_val_fields[*]}"
for field in "${autocomplete_multi_val_fields[@]}"; do

  echo "Adding auto complete field e: ${field}"
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-field\":{
       \"name\":\"${field}_autosuggest_e\",
       \"type\":\"textEdge\",
       \"indexed\":true,
       \"stored\":true,
       \"multiValued\":true
     }
  }" http://$host:$port/solr/$core_name/schema --show-error --fail


  echo "Adding auto complete field wse: ${field}"
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-field\":{
       \"name\":\"${field}_autosuggest_wse\",
       \"type\":\"textWhitespaceEdge\",
       \"indexed\":true,
       \"stored\":true,
       \"multiValued\":true
     }
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

# end for
done

echo "Copying auto complete fields: ${autocomplete_fields[*]}"
for field in "${autocomplete_fields[@]}"; do

  echo "Copying auto complete field e: ${field}"
  # Now configure with the Schema API
  # Modify this with your desired schema configuration
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-copy-field\":{
    \"source\":\"${field}\",
    \"dest\":\"${field}_autosuggest_e\"}
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

  echo "Copying auto complete field wse: ${field}"
  # Now configure with the Schema API
  # Modify this with your desired schema configuration
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-copy-field\":{
    \"source\":\"${field}\",
    \"dest\":\"${field}_autosuggest_wse\"}
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

# end for
done

echo "successfully finished configuring solr schema with the Schema API."
echo "SUCCESS"
