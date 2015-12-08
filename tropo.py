#!/usr/bin/env python

from troposphere import Ref, Template
import troposphere.ec2 as ec2
from troposphere import GetAZs, Parameter, Output, Ref, GetAtt, FindInMap
import sys
t = Template()

count = 0


#Define some things, I think
environmentName = t.add_parameter(Parameter("EnvironmentName", Description="Environment Name",
	Default="Demo",
	Type="String"))
vpn_sg = t.add_parameter(Parameter("vpnsg",
	Description = "VPN SG",
	Type = "String"))

web_sg = t.add_parameter(Parameter("websg", 
	Description="Web ELB SG", 
	Type="String"))

keyname = t.add_parameter(Parameter("demokey", 
	Description="Demo description", 
	Type="String"))

mgmtkey = t.add_parameter(Parameter("mgmtkey",
	Description = "VPN ssh key",
	Type = "String"))

#Define some templates

networktemplate = t.add_parameter(Parameter("networktemplate",
	Description = "URL to Demo VPC Template",
	Type = "String",
	Default = "http://thisisaurl.com"
	))

elbtemplate = t.add_parameter(Parameter("elbtemplate",
	Description = "URL to Demo ELB Template",
	Type = "String",
	Default = "http://thisisaurl.com"
	))

asgtemplate = t.add_parameter(Parameter("asgtemplate",
	Description = "URL to Demo ASG Template",
	Type = "String",
	Default = "http://thisisaurl.com"
	))

#Create access SG
AccessSG = t.add_resource(ec2.SecurityGroup("AccessSG", GroupDescription="Enable SSH access",
	SecurityGroupIngress = [ec2.SecurityGroupRule(
	IpProtocol="tcp",
	FromPort="22",
	ToPort="22",
	CidrIp="0.0.0.0/0",
	)]))
#Create web instances
while count <= 2:
	instance = ec2.Instance("ahdaweb0%s" % count)
	instance.SecurityGroups = [Ref(web_sg), Ref(AccessSG)]
	instance.ImageId = "ami-951945d0"
	instance.InstanceType = "t1.micro"
	instance.KeyName = Ref(keyname)
	instance.Tags = Ref(environmentName)
	instance.AvailabilityZone = GetAZs(Ref("AWS::Region"))
	count += 1
	t.add_resource(instance)

#Create VPN instance
vinstance = ec2.Instance("ahdavpn")
vinstance.SecurityGroups = [Ref(vpn_sg)]
vinstance.ImageId = "ami-951945d0"
vinstance.InstanceType = "t1.micro"
vinstance.KeyName = Ref(mgmtkey)
vinstance.Tags = ["ahda-vpn01"]
vinstance.AvailabilityZone = GetAZs(Ref("AWS::Region"))
t.add_resource(vinstance)
print t.to_json()
