#!/usr/bin/env python

import network
from __init__ import Arguments
from Reader import YAMLReader as reader


shell = Arguments()
args = shell.argumentstuff()

if args.network:
	test = network
	file = args.file[0]
	vpc = test.makeVpc(file)
	vpc.parameters()
	#vpc.createSubnets()
	vpc.createVpc()
	vpc.createInternetGateway()
	vpc.createRoutingTable()
	print vpc.writeTemplateToFile()
