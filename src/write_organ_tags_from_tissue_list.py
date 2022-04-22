# this code will be consolidated into another script or package 
# saving this separately as we work through a long term solution

import csv
import ruamel.yaml

# tissue_list.csv is derived from:
# https://github.com/kharchenkolab/cap-data-clean-up/blob/devel/datasets_description/tissue_dict.json
with open('../collectdata/tissue_list.csv', newline='') as f:
    reader = csv.reader(f)
    tissue_list = [tuple(row) for row in reader]

# ramuel.yaml initialization and configuration
yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)

with open('neo4j2owl-config.yaml') as file:
    yaml_config = yaml.load(file)

# generate dictionary and populate with organ IRIs and labels
organ_labels = {"neo_node_labelling": []}
for organ in organs:
    a = {'classes': organ[0], 'label': organ[1]}
    yaml_config['neo_node_labelling'].append(a)

# export populated dictionary to file
with open('neo4j2owl-config.yaml', 'w') as file:
    documents = yaml.dump(yaml_config, file)