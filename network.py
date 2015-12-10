#!/usr/bin/env python
import random
from troposphere import Ref, Tags, Template, Select
import troposphere.ec2 as ec2
from troposphere import GetAZs, Parameter, Output, Ref, GetAtt, FindInMap
import sys, ipcalc
from netaddr import *
from Reader import YAMLReader as reader
import collections

class makeVpc(object):


	def __init__(self, args):
		self.shell = args
		self.publicsubs = []
		self.privatesubs = []	
		self.t = Template()
		self.file = self.shell
		ireader = reader()
		self.load_file = ireader.loader(self.file)



	#Here we define template parameters

	def parameters(self):
		file = self.load_file
		cidr = file['network']['cidrblock']
		network = file['network']
		reference_list = []
		vpcipblock = self.t.add_parameter(Parameter("VPCIPBLOCK", \
		Description="IP Block for VPC",
		Default=cidr,
		Type="String"))

		EnvName = self.t.add_parameter(Parameter("EnvName", \
		Description="Name of Environment to be deployed.",
		Default=file['cust_id'],
		Type="String"))

		for k,v in network['subnets'].iteritems():
			count = 1
			if v['type'] == "public":
				create_subnets = self.subnetting(network['cidrblock'], v['netmask'])
				while count <= v['count']:
					randomsubnet = random.choice(create_subnets)
					self.subnet = self.t.add_parameter(Parameter("%ssubnet%s" % (k, count), \
					Description="Subnet IP Block",
					Type="String",
					Default=str(randomsubnet)))
					reference_list.append("%ssubnet%s" % (k, count))
					count += 1
			elif v['type'] == "private":
				create_subnets = self.subnetting(network['cidrblock'], v['netmask'])
				while count <= v['count']:
					v['type'], v['count'], count
					randomsubnet = random.choice(create_subnets)
					self.subnet = self.t.add_parameter(Parameter("%ssubnet%s" % (k,count), \
					Description="Private Subnet IP Blocks",
					Type="String",
					Default=str(randomsubnet)))
					reference_list.append("%ssubnet%s" % (k, count))
					count +=1
		create_subnets = self.createSubnets(reference_list)
		template = self.t.to_json()
		return template

	def subnetting(self, cidrBlock, subnets):
		networks = subnets
		cidrblock = cidrBlock
		assigned_subnets = []
		ipnetwork = IPNetwork(cidrBlock)
		subnet_list = ipnetwork.subnet(int(subnets))
		for subnet in subnet_list:
			assigned_subnets.append(subnet)
		return  assigned_subnets
		
	def createSubnets(self, reference_list):
		file = self.load_file
		network = file['network']
		available_zones = GetAZs(Ref("AWS::Region"))
		count = 0
		for reference in reference_list:
			subnet = ec2.Subnet("%s%s" %(count, reference))
			subnet.CidrBlock=Ref(reference)
			subnet.VpcId = Ref("VPC")
			subnet.AvailabilityZone = Select("%s" % count, available_zones)
			self.t.add_resource(subnet)
			#self.t.add_output(Output(Ref(reference), Description = "SubnetId", Value = "Subnet"))
			#self.publicsubs.append("%s%s" %(k, count))
			count +=1
		return self.t.to_json()


	def createVpc(self):
		file = self.load_file
		network = file['network']
		customer = file['cust_id']
		VPC = ec2.VPC("VPC")
		VPC.CidrBlock=Ref("VPCIPBLOCK")
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
