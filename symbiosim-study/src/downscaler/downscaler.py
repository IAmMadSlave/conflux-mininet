#!/bin/python
import networkx as nx

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

net = {}

# parse <model>
tree = ET.ElementTree(file='dumbbell.xml')
root = tree.getroot()

# add topNet to net{} -> { 'topNet': {} }
for child in root:
    net.update({child.attrib.get('name'): {}})
    root = child

# for each net in topNet update net{} -> { 'topNet': {'sub1': {}, 'sub2': {} } }
for child in root:
    if child.attrib.get('type') == 'Net':
        net['topNet'].update({child.attrib.get('name'): {}})

    if child.tag == 'replica':
        net['topNet'].update({child.attrib.get('name'): {}})


print net
