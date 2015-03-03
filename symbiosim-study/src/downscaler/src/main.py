#!/bin/python

import sys
from pprint import pprint
from Parser import Parser

if __name__ == "__main__":
    p = Parser( sys.argv[1] )
    net = p.xml_to_json()
    pprint( net )
