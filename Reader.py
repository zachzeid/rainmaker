#!/usr/bin/env python

import yaml,os,sys

class YAMLReader(object):

	def __init__(self):
		self.file = object


	def loader(self, file):
		f = open(file)
		dataMap = yaml.safe_load(f)
		f.close()
		return dataMap

		








