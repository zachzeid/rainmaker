#!/usr/bin/env python

import makeVpc
from __init__ import Arguments
from Reader import YAMLReader as reader


shell = Arguments()
args = shell.argumentstuff()

if args.network:
	test = makeVpc
	file = args.file[0]
	vpc = test.makeVpc(file)
	vpc.createSubnets()
	vpc.createVpc()
	vpc.createInternetGateway()
	vpc.createRoutingTable()
	#print vpc.writeTemplateToFile()
