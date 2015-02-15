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
        for subchild in child:
            if subchild.attrib.get('type') == 'Host':
                net['topNet'][child.attrib.get('name')].update( {'Host':
                    {'name': subchild.attrib.get('name'), 'interfaces': {} }} )
                for subsubchild in subchild:
                    if subsubchild.attrib.get('type') == 'Interface':
                        net['topNet'][child.attrib.get('name')][subchild.attrib.get('type')]['interfaces'].update(
                                {'name': subsubchild.attrib.get('name')} )
                
            if subchild.attrib.get('type') == 'Router':
                break; 

            if subchild.attrib.get('type') == 'Link':
                break;

    if child.tag == 'replica':
        net['topNet'].update({child.attrib.get('name'): {}})


print net
print net['topNet']['sub1']
