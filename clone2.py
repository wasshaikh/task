import boto3
import botocore.exceptions
client = boto3.client('ec2')
client = boto3.client('autoscaling')
client = boto3.client('elbv2')
security_group = ec2.SecurityGroup('id')

route_table_association = ec2.RouteTableAssociation('id')
	
	ec2 = boto3.resource('ec2', aws_access_key_id='A--AR5Q5--JQRP3IV37M',
	                     aws_secret_access_key='m--xedqF32GsX6--ORsH8px0O3G5ZlreQYNw5QQFm'
	                     region_name='eu-central-1')
	

	# create VPC
	vpc = client.create_vpc(CidrBlock='10.0.0.0/16')
	# we can assign a name to vpc, or any resource, by using tag
	vpc.create_tags(Tags=[{"Key": "vpc", "Value": "default_vpc"}])
	vpc.wait_until_available()
	print(vpc.id)
	
    # create subnet

    subnet = client.create_subnet(CidrBlock = '10.0.1.0/24', VpcId= vpc.id)
    a = print(subnet.id)
    subnet = client.create_subnet(CidrBlock='10.0.2.0/24', VpcId=vpc.id)
	b = print(subnet.id)
    subnet = client.create_subnet(CidrBlock='10.0.3.0/24', VpcId=vpc.id)
	c = print(subnet.id)
    subnet = client.create_subnet(CidrBlock='10.0.4.0/24', VpcId=vpc.id)
	d = print(subnet.id)
    subnet = client.create_subnet(CidrBlock='10.0.5.0/24', VpcId=vpc.id)
	e = print(subnet.id)
    subnet = client.create_subnet(CidrBlock='10.0.6.0/24', VpcId=vpc.id)
	f = print(subnet.id)

	# create then attach vpc to internet gateway
	ig = client.create_internet_gateway()
	vpc.attach_internet_gateway(InternetGatewayId=ig.id)
	print(ig.id)
    
	# create a route table and a public route
	route_table = client.create_route_table()
	route = route_table.create_route(
	    DestinationCidrBlock='0.0.0.0/0',
	    GatewayId=nat_gw.id
    
	)
	print(route_table.id)
	
	# associate the route table with the private subnet
	route_table.associate_with_subnet(SubnetId=[d,e,f])
	

	# Create sec group --public
	sec_group1 = client.create_security_group(
	    GroupName='public_alb_group', Description='Sec group', VpcId=vpc.id)
	sec_group1.authorize_ingress(
	    CidrIp='0.0.0.0/0',
	    IpProtocol='http',
	    FromPort=80,
	    ToPort=80
	)
    sec_group1.authorize_egress(
	    :https, 443, 
        { :group_id => 'private_ec2.id' }
	)
	print(sec_group1.id)

     #  Create sec group --private
    sec_group2 = ec2.create_security_group(
	    GroupName='private_ec2', Description='Sec group', VpcId=vpc.id)
	sec_group2.authorize_ingress(
        CidrIp='0.0.0.0/0',
	    :http, 80, 
        { :group_id => 'public_alb_group.id' }
	)
	print(sec_group2.id)
	
	# Create instance
	instances = ec2.create_instances(
	    ImageId='ami-0db9040eb3ab74509', 
        InstanceType='t2.micro',
	    NetworkInterfaces=[{'SubnetId': d, 'DeviceIndex': 0, 
        'AssociatePublicIpAddress': False, 
        'Groups': [sec_group2.group_id]}])
	    instance.wait_until_running()
        instance.reload()
        print(instance.state)
	    print(instance.id)

    ## launch template contains the user data to launch nginx and attached private SG
    ## and required IAM role
    ## autoscaling group

    response = client.create_auto_scaling_group(
    AutoScalingGroupName='my-auto-scaling-group',
    HealthCheckGracePeriod=300,
    LaunchTemplate={
        'LaunchTemplateId': 'lt-04c0c4bd638d13a31', 
        'Version': '$Latest',
    },
    MaxSize=5,
    MinSize=2,
    DesiredCapacity=3
    TargetGroupARNs=[
        'arn:aws:elasticloadbalancing:eu-central-1:1234--89012:targetgroup/my-targets/73e2d6bc24d8a067',
    ],
    VPCZoneIdentifier= 'd,e,f',
)

print(response)

## Attaches the specified instance to the specified Auto Scaling group
att_ins_asg = client.attach_instances(
    AutoScalingGroupName='my-auto-scaling-group',
    InstanceIds=[
        'ami-0db9040eb3ab74509',
    ],
)
print(att_ins_asg)
## Attaches the specified target group to the specified Auto Scaling group

Att_tg_asg = client.attach_load_balancer_target_groups(
    AutoScalingGroupName='my-auto-scaling-group',
    TargetGroupARNs=[
        'arn:aws:elasticloadbalancing:eu-central-1:1234--89012:targetgroup/my-targets/73e2d6bc24d8a067',
    ],
)

print(Att_tg_asg)

## Attaches the specified load balancer to the specified Auto Scaling group

Att_lb_asg = client.attach_load_balancers(
    AutoScalingGroupName='my-auto-scaling-group',
    LoadBalancerNames=[
        'my-load-balancer',
    ],
)

print(Att_lb_asg)

#elastic_ip and nat gateway

    eip = client.allocate_address(Domain='vpc') 
    nat_gw = client.create_nat_gateway(SubnetId = a,AllocationId = eip.id)

## load balancer and attaching to public subnet and public security group

lb = client.create_load_balancer(
    Name='my-load-balancer',
    Type='application',
    VpcId= 'vpc.id' 
    'SecurityGroups': [
                'public_alb_group.id',
            ],
    Subnets=['a','b','c'],
)

print(lb)

##target group

tg = client.create_target_group(
    Name='my-targets',
    Port=443,
    Protocol='HTTPS',
    VpcId='vpc.id',
)

## register target group

    reg_targets = client.register_targets(TargetGroupArn=tg.Id)

##Listener

Listener = client.create_listener(LoadBalancerArn=lb.Id,
            Protocol='HTTP', Port=80,
            DefaultActions=[{'Type': 'forward',
            'TargetGroupArn': tg.id}])

##lifecyclehook to know details of instance state

Desc_hook = client.describe_lifecycle_hooks(
    AutoScalingGroupName='my-auto-scaling-group',
    LifecycleHookNames='firsthook',
    region='eu-central-1'
)
