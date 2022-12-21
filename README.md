# cap-pipeline-config
Building ontology pipeline configurations for Cell Annotation Platform

## Deployment

### Auto-deployment

Ask admin to grant you with `Storage Object Admin` role.

To auto-deploy solr.json index please keep `gs://cap-gke-rc1-ols/solr/indexes/solr.json` up to date. Every time CAP is deployed
CI/CD pipeline is uses `gs://cap-gke-rc1-ols/solr/indexes/solr.json` to migrate indexes for OLS.

To upload local `solr.json` use the following commands:

    export ENV=[sandbox_env_here]

    gcloud auth login

    gsutil cp solr.json gs://cap-${ENV}-ols/solr/indexes/solr.json

`sandbox_env_here` can be either one of `gke-prod`, `gke-rc1`

### Manual deployment

To access live Solr instance on a GCP project follow instructions described down below in **CAP live Solr instance**.

To deploy initial version of index run the following command:

    ./solr_init.sh -h [HOSTNAME] -p [PORT] -c [COLLECTION]

e.g.

    ./solr_init.sh -h localhost -p 8983 -c ontology

To deploy fresh version of index run the following command:

    ./solr_index.sh -h [HOSTNAME] -p [PORT] -c [COLLECTION]

e.g.

    ./solr_index.sh -h localhost -p 8983 -c ontology


### CAP live Solr instance

Auth into GCP:

    gcloud auth login

List available projects:

    gcloud projects list

Before running further commands connect to remote `solr` instance:

    export PROJECT_ID=[put_you_project_id_here]

e.g.

    export PROJECT_ID=capv2-gke-rc1 # for RC1 taken from `gcloud projects list`

    export PROJECT_ID=capv2-gke-prod # for Prod taken from `gcloud projects list`

Connect to solr:

    ES_INSTANCE_NAME=$(gcloud compute instances list --project $PROJECT_ID | grep solr | awk '{ print $1 }')

    ES_INSTANCE_REGION=$(gcloud compute instances list --project $PROJECT_ID | grep solr | awk '{ print $2 }')

    gcloud compute ssh --project $PROJECT_ID --ssh-flag="-L 8984:localhost:8983" --zone $ES_INSTANCE_REGION $ES_INSTANCE_NAME
