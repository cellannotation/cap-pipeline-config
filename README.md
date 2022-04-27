# cap-pipeline-config
Building ontology pipeline configurations for Cell Annotation Platform

## Deployment

To deploy initial version of index run the following command:

    ./solr_init.sh -h [HOSTNAME] -p [PORT] -c [COLLECTION]

e.g.

    ./solr_init.sh -h localhost -p 8983 -c ontology

To deploy fresh version of index run the following command:

    ./solr_index.sh -h [HOSTNAME] -p [PORT] -c [COLLECTION]

e.g.

    ./solr_index.sh -h localhost -p 8983 -c ontology
