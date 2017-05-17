#!/usr/bin/python
##___AUTHOR : RUDHRA RAI___ ##

''' This Script creates cluster for setting up the datashop
	this includes vpc, internet gateway, public and private
	subnets,route tables for public and private subnets, 
	and routes in them, security groups and security rules
	are defined'''


import boto3
import json
import os
import logging
#from security_group_and_rules import create_security_group
client = boto3.client('ec2')
ownerName="Rudhra"
projectName='rudhra-cluster'

'''This function creates vpc,
	provide project name(for specifying the name of project) 
		and cidr value(for specifying the size of project),
	returns vpc id'''
def create_vpc(projectName,vpcCidr):
	response = client.create_vpc(CidrBlock=vpcCidr)
	vpcid=response['Vpc']['VpcId']
	create_tags(vpcid,projectName)
	msg="VPC created with vpc id: "+vpcid
	logger(msg)
	return vpcid
	# vpc id-> vpc-11b71978


''' This function creates subnet,
	provide subnet name(for naming the subnet) 
		and cidr value(for specifing the size of subnet)
		and vpc id(to provide details of vpc such that, in which vpc subnet needs to be launched),
	returns subnet id'''
def create_subnet(vpcid,subnet_name,cidr):
	response = client.create_subnet(VpcId=vpcid,CidrBlock=cidr)
	subnetid=response['Subnet']['SubnetId']
	create_tags(subnetid, subnet_name)
	msg="subnet created with subnet id: "+subnetid
	logger(msg)
	return subnetid
	# public subnet id-> subnet-9a6cd2f3
	# private subnet id-> subnet-106dd379


''' This function creates internet gateway,
	provide internet gateway name(to specify gateway name),
	returns internet gateway id'''
def create_internet_gateway(igw_name):
	response = client.create_internet_gateway()
	InternetGatewayId=response['InternetGateway']['InternetGatewayId']
	create_tags(InternetGatewayId, igw_name)
	msg="Internet Gateway Created with internet gateway id: "+InternetGatewayId
	logger(msg)
	return InternetGatewayId
	# internet gateway id->igw-8672a1ef


''' This function attaches internet gateway to specified vpc,
	provide internet gateway id and vpc id,
	returns nothing'''
def attach_internet_gateway(igwId,vpcid):
	response = client.attach_internet_gateway(InternetGatewayId=igwid,VpcId=vpcid)
	msg="internet gateway has been attached to vpc"
	logger(msg)


''' This function generates an elastic ip for the vpc
	provide nothing
	returns public ip and allocation id'''
def allocate_elastic_address_vpc():
	response = client.allocate_address(
	Domain='vpc'
	)
	elastic=[response['AllocationId'],response['PublicIp']]
	msg="Elatic ip generated with address: "+response['PublicIp']+" Allocation id is: "+response['AllocationId']
	logger(msg)
	return elastic

''' This function creates nat gateway for accessing internet by private subnet instances
	provide subnet id(in which subnet nat gateway will reside)
		and allocation id(for specifying elastic ip)
	returns nat gatway id'''
def create_nat_gateway(subnetid,allocationid):
	response = client.create_nat_gateway(
	AllocationId=allocationid,
	SubnetId=subnetid,
	)
	nat_gateway_id=response['NatGateway']['NatGatewayId']
	msg="nat gateway created with nat gateway id: "+nat_gateway_id
	logger(msg)
	return nat_gateway_id

''' This function creates route table 
	provide vpc id(in which vpc route table needs to be created)
		and route table name(to specify route table name)
		returns route table id'''
def create_route_table(vpcid, rtb_name):
	response = client.create_route_table(VpcId=vpcid)
	route_table_id=response['RouteTable']['RouteTableId']
	create_tags(route_table_id, rtb_name)
	msg="route table created with route table id: "+route_table_id
	logger(msg)
	return route_table_id
	#public rtbid-> rtb-47cc7b2e
	#private rtbid-> rtb-c6cc7baf


''' This function creates route for public route table
	provide route table id(to specify in which route table route has been applied)
		and destination cidr block (to specify the traffic such that from  where traffic should be allowed)
		and intenet gateway id(to add it in route so that the route table can be configured to accept internet traffic)
	returns nothing'''
def create_public_route(rtbid,destCidrBlock,igwid):
	response = client.create_route(
	RouteTableId=rtbid,
	DestinationCidrBlock=destCidrBlock,
	GatewayId=igwid
	)
	msg="route created with internet gateway"
	logger(msg)


''' This function creates route for public route table
	provide route table id(to specify in which route table route has been applied)
		and destination cidr block (to specify the traffic, such that, from  where traffic should be allowed)
		and nat gateway id(to add it in route so that the route table can be configured to accept traffic from nat gateway only)
	returns nothing'''
def create_private_route(rtbid,destCidrBlock,natid):
	response = client.create_route(
	RouteTableId=rtbid,
	DestinationCidrBlock=destCidrBlock,
	NatGatewayId=natid
	)
	msg="route created with NAT gateway"
	logger(msg)


''' This function associates the route table to subnet
	provide subnet id(for which subnet route table needs to be associated)
		and route table id(which route table needs to be associated)
	returns association id'''
def associate_route_table(subnetid,rtbid):
	response = client.associate_route_table(
	SubnetId=subnetid,
	RouteTableId=rtbid
	)
	associationid=response['AssociationId']
	msg="route table associted with the subsequent subnet with association id: "+associationid
	logger(msg)
	return associationid


''' This function creates security group in the vpc
	provide security group name(for naming the group used for tagging)
		and group name(for specifying the group name)
		and description(for giving the description of group)
		and vpc id(in which vpc security group needs to be made)
	returns security group id'''
def create_security_group(sgname,grpname,desc,vpcid):
	response = client.create_security_group(
	GroupName=grpname,
	Description=desc,
	VpcId=vpcid
	)
	security_group_id=response['GroupId']
	create_tags(security_group_id, sgname)
	msg="security group created by the owner with group id: "+security_group_id
	logger(msg)
	return security_group_id


''' This function creates security rule to put in security group
	provide type(which type of rule)
		and port range 
		and security group id(for which security group needs to be applied)
		and ip protocol(tcp)
		and cidr ip(from where traffic is allowed)
	returns nothing'''
def inbound_security_group_rule(type,port,sggroupid,ip_protocol,cidrip):
	response = client.authorize_security_group_ingress(
	GroupId=sggroupid,
	IpProtocol=ip_protocol,
	FromPort=port,
	ToPort=port,
	CidrIp=cidrip
	)
	msg="inbound security rule created for: "+type
	logger(msg)

''' This function create key pair for signing into instance
	provide keyname(for specifying the name)
	returns nothing'''
def create_key_pair(keyname):
	response = client.create_key_pair(KeyName=keyname)
	f = open( keyname+'.pem', 'w' )
	f.write(response['KeyMaterial'])
	f.close()
	os.chmod(keyname+".pem",400)
	msg="Pem file created with file name: "+keyname+".pem"
	logger(msg)


# def create_network_interface(subnetid,sggroup,publicip_association)
# 	interfaceSpec = client.networkinterface.NetworkInterfaceSpecification(subnet_id=subnetid,
# 																	groups=[sggroup],
# 																	associate_public_ip_address=publicip_association)
# 	interfaces = client.networkinterface.NetworkInterfaceCollection(interfaceSpec)


''' This function creates an instance
	provide server name
		and image id
		and count
		and pemfileName
		and security group id
		and userdata 
		and instance type
	public subnet id
		provide subnet id
	ebs block details
		provide virtual name
		and device name
		and volume size
		and volume types'''
def create_instance(server_name,imageid,count,pemFileName,sggroupid,userdata,instanceType,subnetid,virtual_name,device_name,volumesize,volumetype,iops):#,privateipaddress):
	response = client.run_instances(
	ImageId=imageid,
	MinCount=count,
	MaxCount=count,
	KeyName=pemFileName,
	SecurityGroupIds=[
		sggroupid,
	],
	UserData=userdata,
	InstanceType=instanceType,
	#'t1.micro'|'t2.nano'|'t2.micro'|'t2.small'|'t2.medium'|'t2.large'|'t2.xlarge'|'t2.2xlarge'|'m1.small'|'m1.medium'|'m1.large'|'m1.xlarge'|'m3.medium'|'m3.large'|'m3.xlarge'|'m3.2xlarge'|'m4.large'|'m4.xlarge'|'m4.2xlarge'|'m4.4xlarge'|'m4.10xlarge'|'m4.16xlarge'|'m2.xlarge'|'m2.2xlarge'|'m2.4xlarge'|'cr1.8xlarge'|'r3.large'|'r3.xlarge'|'r3.2xlarge'|'r3.4xlarge'|'r3.8xlarge'|'r4.large'|'r4.xlarge'|'r4.2xlarge'|'r4.4xlarge'|'r4.8xlarge'|'r4.16xlarge'|'x1.16xlarge'|'x1.32xlarge'|'i2.xlarge'|'i2.2xlarge'|'i2.4xlarge'|'i2.8xlarge'|'i3.large'|'i3.xlarge'|'i3.2xlarge'|'i3.4xlarge'|'i3.8xlarge'|'i3.16xlarge'|'hi1.4xlarge'|'hs1.8xlarge'|'c1.medium'|'c1.xlarge'|'c3.large'|'c3.xlarge'|'c3.2xlarge'|'c3.4xlarge'|'c3.8xlarge'|'c4.large'|'c4.xlarge'|'c4.2xlarge'|'c4.4xlarge'|'c4.8xlarge'|'cc1.4xlarge'|'cc2.8xlarge'|'g2.2xlarge'|'g2.8xlarge'|'cg1.4xlarge'|'p2.xlarge'|'p2.8xlarge'|'p2.16xlarge'|'d2.xlarge'|'d2.2xlarge'|'d2.4xlarge'|'d2.8xlarge'|'f1.2xlarge'|'f1.16xlarge',
  
	BlockDeviceMappings=[
		{
			'VirtualName': virtual_name,
			'DeviceName': device_name,
			'Ebs': {
				'VolumeSize': volumesize,
				'DeleteOnTermination': False,
				'VolumeType': volumetype,
				#'Iops': iops,
				#'Encrypted': False
			},
			# 'NoDevice': 'string'
		},
	],
	Monitoring={
		'Enabled': True
	},
	SubnetId=subnetid,
	DisableApiTermination=True,
	#InstanceInitiatedShutdownBehavior='stop',
	# PrivateIpAddress=privateipaddress,
	# NetworkInterfaces=[
	#     {
	#         'NetworkInterfaceId': 'string',
	#         'DeviceIndex': 123,
	#         'SubnetId': 'string',
	#         'Description': 'string',
	#         'PrivateIpAddress': 'string',
	#         'Groups': [
	#             'string',
	#         ],
	#         'DeleteOnTermination': True|False,
	#         'PrivateIpAddresses': [
	#             {
	#                 'PrivateIpAddress': 'string',
	#                 'Primary': True|False
	#             },
	#         ],
	#         'SecondaryPrivateIpAddressCount': 123,
	#         'AssociatePublicIpAddress': True|False,
	#     },
	# ],
	# IamInstanceProfile={
	#     'Arn': 'string',
	#     'Name': 'string'
	# },
	#EbsOptimized=True|False
	)
	instanceid = response['Instances'][0]['InstanceId']
	privateip = response['Instances'][0]['PrivateIpAddress']
	#publicip = response['Instances'][0]['PublicIpAddress']
	create_tags(instanceid,server_name)
	msg="instance created with instance id: "+instanceid+" and private ip "+privateip#+" and public ip "+publicip
	logger(msg)
	return instanceid


''' This function associates elastic ip to an instance
	provide elastic allocation id
		and instance id
	returns allocation id'''
def associate_ip_address(elastic_allocationid,instanceid):
	response = client.associate_address(
	AllocationId=elastic_allocationid,
	InstanceId=instanceid,
	)
	associationid=response['AssociationId']
	msg="elastic ip associated having instance id: "+instanceid+" with allocation id: "+associationid
	logger(msg)
	return associationid

''' This function creates tags for the resouces
	provide resouce id(to specify, for which resource tagging needs to be done)
		and value(what should be the name)
	returns name'''
def create_tags(resourceid,value):
	response = client.create_tags(
	Resources=[resourceid],
	Tags=[
		{
			'Key': 'Name',
			'Value': value
		},
		{
			'Key': 'Project',
			'Value': projectName
		},
		{
			'Key': 'Owner',
			'Value': ownerName
		}
	])


''' This fucntion logs all the activities into a log file
	provide msg value(to log it into the file)
	returns nothing'''
def logger(msg):
	print msg
	logging.basicConfig(filename='project.log', level=logging.INFO, format='%(asctime)s %(message)s')
	logging.info(msg)

if __name__ == '__main__':

	# vpc details
	vpcCidr='10.0.0.0/16'

	# subnet details
	publicCidr='10.0.0.0/24'
	privateCidr='10.0.1.0/24'

	# security group details
	destCidrBlock="0.0.0.0/0"

	sgnametag="rudhra"
	security_group_name="rudhra-security-group"
	sg_description="security group made by rudhra"

	#inbound security rules detail
	security_cidrip="0.0.0.0/0"

	## public inbound security rules detail
	public_ip_protocol="tcp"
	public_port={'ssh':22,'http':80,'https':443}

	# ###  private inbound security rules detail
	# ## private_ip_protocol=['all']
	# ## private_port={'ALL_Traffic':None}
	# ## cidrip="0.0.0.0/0"

	logger('Cluster Creation Started')

	vpcid=create_vpc(projectName,vpcCidr)
	#vpcid="vpc-11b71978"
	
	public_subnetid=create_subnet(vpcid,projectName+" Public subnet",publicCidr)
	#public_subnetid="subnet-9a6cd2f3"
	private_subnetid=create_subnet(vpcid,projectName+" Private subnet",privateCidr)
	#private_subnetid="subnet-106dd379"
	
	igwid=create_internet_gateway(projectName+" Internet gateway")
	#igwid="igw-8672a1ef"
	attach_internet_gateway(igwid,vpcid)

	elastic=allocate_elastic_address_vpc()
	elastic_allocationid=elastic[0][0]
	elastic_publicip=elastic[1][0]
	#elastic_publicip="52.14.145.178"
	#elastic_allocationid="eipalloc-5d5b8034"

	nat_gateway_id=create_nat_gateway(public_subnetid,elastic_allocationid)
	#old nat_gateway_id="nat-03cd9d58905b56049" deleted
	#nat_gateway_id="nat-00bf625cd793bba52"
	
	publicrtbid=create_route_table(vpcid,projectName+" public route table")
	#publicrtbid="rtb-47cc7b2e"
	privatertbid=create_route_table(vpcid,projectName+" private route table")
	#privatertbid="rtb-c6cc7baf"
	
	create_public_route(publicrtbid,destCidrBlock,igwid)
	create_private_route(privatertbid,destCidrBlock,nat_gateway_id)
	public_asso_rtb_id=associate_route_table(public_subnetid,publicrtbid)
	#public_asso_rtb_id="rtbassoc-45d9572c"
	private_asso_rtb_id=associate_route_table(private_subnetid,privatertbid)
	#private_asso_rtb_id="rtbassoc-7f3db316"
	
	sggroupid=create_security_group(sgnametag,security_group_name,sg_description,vpcid)
	#sggroupid="sg-0268fe6b"

	inbound_security_group_rule("ssh",public_port['ssh'],sggroupid,public_ip_protocol,security_cidrip)
	inbound_security_group_rule("http",public_port['http'],sggroupid,public_ip_protocol,security_cidrip)
	inbound_security_group_rule("https",public_port['https'],sggroupid,public_ip_protocol,security_cidrip)
	# inbound_security_group_rule("ALL Traffic",private_port['ALL_Traffic'],sggroupid,private_ip_protocol,security_cidrip) 
	
	create_key_pair(projectName)
	
	#ohio_ami_id_centos='ami-6a2d760f'
	north_verginia_ami_id_centos='ami-6d1c2007'
	pemfile=projectName
	server1={'server_name':projectName+" rudhra-server1",'imageid':north_verginia_ami_id_centos,'count':1,
	  'pemFileName':pemfile,'sggroupid':sggroupid,'userdata':"file.sh",
	  'instanceType':'t2.nano','subnetid':public_subnetid,'ebs_virtual_name':"basic ebs",
	  'ebs_device_name':"/dev/sda1",'ebs_volumesize':500,'ebs_volumetype':"gp2",'ebs_iops':1500}
	#   #'privateipaddress':'0'}

	instanceid=create_instance(server1['server_name'],server1['imageid'],server1['count'],server1['pemFileName'],
	  server1['sggroupid'],server1['userdata'],server1['instanceType'],server1['subnetid'],
	  server1['ebs_virtual_name'],server1['ebs_device_name'],server1['ebs_volumesize'],
	  server1['ebs_volumetype'],server1['ebs_iops'])#,server1['privateipaddress'])
	#instanceid='i-0a38df55eb4999661'

	#associationid=associate_ip_address(elastic_allocationid,instanceid)

	logger('Cluster Creation Finished')




