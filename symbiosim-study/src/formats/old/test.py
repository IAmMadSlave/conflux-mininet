#!/bin/python

import json

json_file = open( 'downscaled_topology.json' )
json_data = json.load( json_file )

link_table = []

for link in json_data['net']['links']:
    link_table.append(link['name']) 

for element in link_table:
    print element
