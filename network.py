#!/usr/bin/env python
import random
from troposphere import Ref, Tags, Template, Select
import troposphere.ec2 as ec2
from troposphere import GetAZs, Parameter, Output, Ref, GetAtt, FindInMap
import sys, ipcalc
from netaddr import *
from Reader import YAMLReader as reader
class makeVpc(object):


	def __init__(self, args):
		self.shell = args
		self.publicsubs = []
		self.privatesubs = []	
		self.t = Template()
		self.file = self.shell
		ireader = reader()
		self.load_file = ireader.loader(self.file)


	def subnetting(self, cidrBlock, subnets):
		networks = subnets
		cidrblock = cidrBlock
		assigned_subnets = []
		ipnetwork = IPNetwork(cidrBlock)
		subnet_list = ipnetwork.subnet(int(subnets))
		for subnet in subnet_list:
			assigned_subnets.append(subnet)
		return  assigned_subnets
		
	def createSubnets(self):
		file = self.load_file
		network = file['network']
		available_zones = GetAZs(Ref("AWS::Region"))
		for k,v in network['subnets'].iteritems():
			count = 0
			if v['type'] == "public":
				create_subnets = self.subnetting(network['cidrblock'], v['netmask'])
				while count < v['count']:
					subnet = ec2.Subnet("%s%s" % (k, count))
					random_subnets = random.choice(create_subnets)
					create_subnets.remove(random_subnets)
					subnet.CidrBlock=str(random_subnets)
					subnet.VpcId = Ref("VPC")
					
					subnet.AvailabilityZone = Select("%s" % count, available_zones)
					self.t.add_resource(subnet)
					self.t.add_output(Output("%s%s" % (k, count), Description = "SubnetId", Value=Ref(subnet)))
					self.publicsubs.append("%s%s" %(k, count))
					count += 1
			elif v['type'] == "private":
				create_subnets = self.subnetting(network['cidrblock'], v['netmask'])
				while count < v['count']:
					subnet = ec2.Subnet("%s%s" % (k, count))
					random_subnets = random.choice(create_subnets)
					create_subnets.remove(random_subnets)
					subnet.CidrBlock=str(random_subnets)
					stuff = subnet.CidrBlock.split("/")
					print stuff[0]
					subnet.VpcId = Ref("VPC")
					subnet.AvailabilityZone = Select("%s" % count, available_zones)
					self.t.add_resource(subnet)
					self.t.add_output(Output("%s%s" % (k, count), Description = "SubnetId", Value=Ref(subnet)))
					self.privatesubs.append(subnet)
					count += 1
			else:
				print "There seems to be an error, check your YAML file."
		return self.t.to_json()


	def createVpc(self):
		file = self.load_file
		network = file['network']
		customer = file['cust_id']
		VPC = ec2.VPC("VPC")
		VPC.CidrBlock=network['cidrblock']
		VPC.Tags=Tags(Name=customer)
		self.t.add_resource(VPC)
		return self.t.to_json()

	def createInternetGateway(self):
		igw = ec2.InternetGateway('InternetGateway')
		self.t.add_resource(igw)
		igwAttachment = ec2.VPCGatewayAttachment('AttachGateway',
			VpcId=Ref("VPC"),
			InternetGatewayId=Ref(igw)
			)
		self.t.add_resource(igwAttachment)
		return self.t.to_json()

	def createRoutingTable(self):
		count = 0
		a_list = []
		file = self.load_file
		network = file['network']['subnets']
		for k, v in network.iteritems():
			if v['type'] not in a_list:
				a_list.append(v['type'])
		
		for type in a_list:
			if type == "public":
				public_rt = ec2.RouteTable("publicRoute")
				public_rt.VpcId = Ref("VPC")
				public_rt.Tags=Tags(Name="publicRouteTable")
				self.t.add_resource(public_rt)
			elif type == "private":
				private_rt = ec2.RouteTable("privateRoute")
				private_rt.VpcId = Ref("VPC")
				private_rt.Tags=Tags(Name="privateRouteTable")
				self.t.add_resource(private_rt)
		
		for pubsub in self.publicsubs:
			pub = ec2.SubnetRouteTableAssociation("pubsub%s" % count)
			pub.SubnetId = Ref(pubsub)
			pub.RouteTableId = Ref("publicRoute")
			self.t.add_resource(pub)
			count = count + 1
		for privsub in self.privatesubs:
			priv = ec2.SubnetRouteTableAssociation("privsub%s" % count)
			priv.SubnetId = Ref(privsub)
			priv.RouteTableId = Ref("privateRoute")
			self.t.add_resource(priv)
			count = count + 1
		return self.t.to_json()

	
	def writeTemplateToFile(self):
		return self.t.to_json()