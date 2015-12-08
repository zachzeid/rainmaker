#!/usr/bin/env python

import argparse


class Arguments(object):
	def __init__(self):
		self.foo = "bar"
	def argumentstuff(self):
		parser = argparse.ArgumentParser(description="Make magic")
		parser.add_argument('-f', '--file', nargs="*", required=True)
		parser.add_argument('-n', '--network', action='store_true', required=True)
		parser.add_argument('-a', '--application', action='store_true', required=False)
		parser.add_argument('-s', '--security', action='store_true', required=False)

		args = parser.parse_args()
		return args
