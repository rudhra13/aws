import boto3
client = boto3.client('ec2')

def create_security_group(sgname,grpname,desc,vpcid):
	response = client.create_security_group(
	GroupName=grpname,
	Description=desc,
	VpcId=vpcid
	)
	security_group_id=response['GroupId']
	create_tags(security_group_id, sgname)
	print "security group created by the owner with group id: "+security_group_id
	return security_group_id

def inbound_security_group_rule(type,port,sggroupid,ip_protocol,cidrip):
	response = client.authorize_security_group_ingress(
    GroupId=sggroupid,
    IpProtocol=ip_protocol,
    FromPort=port[0],
    ToPort=port[0],
    CidrIp=cidrip,
	)
	msg="inbound security rule created for: "+type
	print msg
	# logger(msg)

sggroupid="sg-0268fe6b"
ip_protocol="tcp"
# porthttp=[80,80]
#portssh=[22,22]
# porthttps=[443,443]
port={'ssh':[22,22],'http':[80,80],'https':[443,443]}
cidrip="0.0.0.0/0"


inbound_security_group_rule("ssh",port['ssh'],sggroupid,ip_protocol,cidrip)
inbound_security_group_rule("http",port['http'],sggroupid,ip_protocol,cidrip)
inbound_security_group_rule("https",port['https'],sggroupid,ip_protocol,cidrip)

