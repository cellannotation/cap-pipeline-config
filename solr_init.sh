#!/bin/bash


echo "Indexing ontology collection in server localhost:8993"
curl --location --request POST 'http://localhost:8993/solr/ontology/update/json?commit=true' --header 'Content-Type: application/json' --data-binary '@solr.json'

echo "Configuring ontology schema in server localhost:8993"
bash solr.config.sh -h localhost -p 8993

echo "Re-indexing ontology collection in server localhost:8993"
curl --location --request POST 'http://localhost:8993/solr/ontology/update/json?commit=true' --header 'Content-Type: application/json' --data-binary '@solr.json'
