import ssm
import pulumi
import pulumi_aws as aws
from pulumi import export

tagged={"Type": "SandboxVPC","Environment":"Sandbox"}

# /STACK/ENVIRONMENT/REGION/RESOURCE

def create_vpc(vpcData, vpcRegion):

    VPC = aws.ec2.Vpc(vpcData["vpcName"],
        cidr_block=vpcData["vpcCIDR"],
        enable_dns_support=True, # gives you an internal domain name
        enable_dns_hostnames=True, # gives yoiu an internal host name
        instance_tenancy="default",
        tags = tagged|{"Name":f"{vpcData['vpcName']}"},
        opts=pulumi.ResourceOptions(provider=vpcRegion))
    export(f"{vpcData['vpcName']}-vpcid",VPC.id)
    ssm.AddIdToSSM(vpcData["vpcName"], f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/vpcid", VPC.id, tagged|{"Name":f"{vpcData['vpcName']}"}, vpcRegion)
    return VPC


def create_subnets(vpcData, vpcRegion):
    # Generate NAT and IGW gateways
    vpcId = ssm.GetIdFromSSM(f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/vpcid", vpcRegion)
    igw = aws.ec2.InternetGateway(f"igw-{vpcData['vpcName']}", vpc_id=vpcId, tags = tagged|{"Name":f"{vpcData['vpcName']} Internet Gateway"},opts=pulumi.ResourceOptions(provider=vpcRegion))
    ssm.AddIdToSSM(f"{vpcData['vpcName']}-igw", f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/vpcIGWid", igw.id, tagged|{"Name":f"{vpcData['vpcName']}"}, vpcRegion)
    eip = aws.ec2.Eip(f"{vpcData['vpcName']} Address", domain="vpc", tags = tagged|{"Name":f"{vpcData['vpcName']} Gateway EIP"},opts=pulumi.ResourceOptions(provider=vpcRegion))

    # Generate Route Tables
    public_rt = aws.ec2.RouteTable(f"{vpcData['vpcName']}-public-rt",
        vpc_id=vpcId,
        routes=[aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id
        )], 
        tags = tagged|{"Name":f"{vpcData['vpcName']} Public Route table"},opts=pulumi.ResourceOptions(provider=vpcRegion))

    public_nets = 0
    for subnets in vpcData['subnets']:
        if subnets['type'] == "IGW":
            pub_subnet = aws.ec2.Subnet(f"{vpcData['vpcName']}-{subnets['name']}",vpc_id=vpcId, cidr_block=subnets["cidr"], map_public_ip_on_launch=True, availability_zone=subnets['zone'], tags = tagged|{"Name":f"{vpcData['vpcName']} {subnets['name']}"},opts=pulumi.ResourceOptions(provider=vpcRegion))
            aws.ec2.RouteTableAssociation(f"{vpcData['vpcName']} {subnets['name']} public-route", subnet_id=pub_subnet.id, route_table_id=public_rt.id, opts=pulumi.ResourceOptions(depends_on=[public_rt],provider=vpcRegion))
            if public_nets == 0:
                nat = aws.ec2.NatGateway(f"{vpcData['vpcName']}-nat-gateway", allocation_id=eip.id, subnet_id=pub_subnet.id, tags = tagged|{"Name":f"{vpcData['vpcName']} NAT Gateway"},opts=pulumi.ResourceOptions(provider=vpcRegion))
            public_nets = public_nets + 1
            ssm.AddIdToSSM(f"{vpcData['vpcName']}-public{public_nets}", f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/subnets/public{public_nets}", pub_subnet.id, tagged|{"Name":f"{vpcData['vpcName']}"}, vpcRegion)   

    # Nat Gateway requires the first public subnet ID to attach to
    private_rt = aws.ec2.RouteTable(f"{vpcData['vpcName']}-private-rt",
        vpc_id=vpcId,
        routes=[aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id=nat.id,
        )],
        tags = tagged|{"Name":f"{vpcData['vpcName']} Private Route Table"},
        opts=pulumi.ResourceOptions(depends_on=[nat],provider=vpcRegion))  

    private_nets = 0
    for subnets in vpcData['subnets']:
        if subnets['type'] == "NAT":
            private_subnet = aws.ec2.Subnet(f"{vpcData['vpcName']}-{subnets['name']}",vpc_id=vpcId, cidr_block=subnets["cidr"], map_public_ip_on_launch=False, availability_zone=subnets['zone'], tags = tagged|{"Name":f"{vpcData['vpcName']} {subnets['name']}"},opts=pulumi.ResourceOptions(provider=vpcRegion))
            aws.ec2.RouteTableAssociation(f"{vpcData['vpcName']} {subnets['name']} private-route", subnet_id=private_subnet.id, route_table_id=private_rt.id, opts=pulumi.ResourceOptions(depends_on=[nat],provider=vpcRegion))
            if private_nets == 0:
                privSubnet = private_subnet
            private_nets = private_nets + 1   
            ssm.AddIdToSSM(f"{vpcData['vpcName']}-private{private_nets}", f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/subnets/private{private_nets}", private_subnet.id, tagged|{"Name":f"{vpcData['vpcName']}"}, vpcRegion)   
    return privSubnet


def create_peering(requester_id, accepter_id, caRegion):

    # Create a peering connection from requester to accepter
    vpc_peering_connection = aws.ec2.VpcPeeringConnection("vpcPeeringConnection",
        vpc_id=requester_id,                # ID of the requester VPC
        peer_vpc_id=accepter_id,            # ID of the VPC with which you are creating the VPC Peering Connection
        peer_region="ca-central-1",
        auto_accept=False,
    )

    # Accepter's side of the connection.
    aws.ec2.VpcPeeringConnectionAccepter("peeringConnectionAccepter",
        vpc_peering_connection_id=vpc_peering_connection.id,
        auto_accept=True,
        opts=pulumi.ResourceOptions(provider=caRegion))

    # Export the ID of the VPC Peering Connection
    pulumi.export('peeringID', vpc_peering_connection.id)
    # ssm.AddIdToSSM("VPC-Peering-ID", f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/subnets/public{public_nets}", pub_subnet.id, tagged|{"Name":f"{vpcData['vpcName']}"}, vpcRegion)   

