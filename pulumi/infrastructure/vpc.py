import time
import pulumi
import pulumi_aws as aws
from pulumi import export

tagged={"Type": "SandboxVPC","Environment":"Sandbox"}

def create_vpc(vpcData, vpcRegion):

    VPC = aws.ec2.Vpc(vpcData["vpcName"],
    cidr_block=vpcData["vpcCIDR"],
    enable_dns_support=True, # gives you an internal domain name
    enable_dns_hostnames=True, # gives yoiu an internal host name
    instance_tenancy="default",
    tags = tagged|{"Name":f"{vpcData['vpcName']} Gateway EIP"},opts=pulumi.ResourceOptions(provider=vpcRegion))
    export(f"{vpcData['vpcName']}-vpcid",VPC.id)

    # Dynamically fetch AZs so we can spread across them.
    availability_zones = aws.get_availability_zones()

    # Generate NAT and IGW gateways
    igw = aws.ec2.InternetGateway("igw", vpc_id=VPC.id, tags = tagged|{"Name":f"{vpcData['vpcName']} Internet Gateway"},opts=pulumi.ResourceOptions(provider=vpcRegion))
    eip = aws.ec2.Eip(f"{vpcData['vpcName']} Address", domain="vpc", tags = tagged|{"Name":f"{vpcData['vpcName']} Gateway EIP"},opts=pulumi.ResourceOptions(provider=vpcRegion))

    # Generate Route Tables
    public_rt = aws.ec2.RouteTable("public-rt",
        vpc_id=VPC.id,
        routes=[aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id
        )], 
        tags = tagged|{"Name":f"{vpcData['vpcName']} Public Route table"},opts=pulumi.ResourceOptions(provider=vpcRegion))

    public_nets = 0
    for subnets in vpcData['subnets']:
        if subnets['type'] == "IGW":
            pub_subnet = aws.ec2.Subnet(subnets["name"],vpc_id=VPC.id, cidr_block=subnets["cidr"], map_public_ip_on_launch=True, availability_zone=availability_zones.names[public_nets], tags = tagged|{"Name":f"{vpcData['vpcName']} Public Subnet"},opts=pulumi.ResourceOptions(provider=vpcRegion))
            aws.ec2.RouteTableAssociation(f"{subnets['name']} public-route", subnet_id=pub_subnet.id, route_table_id=public_rt.id, opts=pulumi.ResourceOptions(depends_on=[public_rt],provider=vpcRegion))
            if public_nets == 0:
                nat = aws.ec2.NatGateway("nat-gateway", allocation_id=eip.id, subnet_id=pub_subnet.id, tags = tagged|{"Name":f"{vpcData['vpcName']} NAT Gateway"},opts=pulumi.ResourceOptions(provider=vpcRegion))
            public_nets = public_nets + 1

    # Nat Gateway requires the first public subnet ID to attach to
    private_rt = aws.ec2.RouteTable("private-rt",
        vpc_id=VPC.id,
        routes=[aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id=nat.id,
        )],
        tags = tagged|{"Name":f"{vpcData['vpcName']} Private Route Table"},
        opts=pulumi.ResourceOptions(depends_on=[nat],provider=vpcRegion))  

    private_nets = 0
    for subnets in vpcData['subnets']:
        if subnets['type'] == "NAT":
            private_subnet = aws.ec2.Subnet(subnets["name"],vpc_id=VPC.id, cidr_block=subnets["cidr"], map_public_ip_on_launch=False, availability_zone=availability_zones.names[private_nets], tags = tagged|{"Name":f"{vpcData['vpcName']} Private Subnet"},opts=pulumi.ResourceOptions(provider=vpcRegion))
            aws.ec2.RouteTableAssociation(f"{subnets['name']} private-route", subnet_id=private_subnet.id, route_table_id=private_rt.id, opts=pulumi.ResourceOptions(depends_on=[nat],provider=vpcRegion))
            private_nets = private_nets + 1            


def create_peering(requester_id, accepter_id):

    # Create a peering connection from requester to accepter
    vpc_peering_connection = aws.ec2.VpcPeeringConnection("vpcPeeringConnection",
        vpc_id=requester_id,                # ID of the requester VPC
        peer_vpc_id=accepter_id,            # ID of the VPC with which you are creating the VPC Peering Connection
        auto_accept=True
    )

    # Export the ID of the VPC Peering Connection
    pulumi.export('peeringID', vpc_peering_connection.id)