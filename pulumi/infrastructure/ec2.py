import pulumi
import pulumi_aws as aws
import ssm

def create_sg(sgData,awsRegion, Region, vpc):
    secGroupIds = {}
    for group in sgData['groups']:
        ingressSet = []
        for rule in group['rules']:  
            ingressSet.append(aws.ec2.SecurityGroupIngressArgs( protocol=rule['protocol'], from_port=rule['from_port'], to_port=rule['to_port'], cidr_blocks=[rule['cidr']]))

        secGroup = aws.ec2.SecurityGroup(f"{group['groupName']}-{Region}",
            ingress=ingressSet,
            egress=[aws.ec2.SecurityGroupEgressArgs(
                from_port=0,
                to_port=0,
                protocol="-1",
                cidr_blocks=["0.0.0.0/0"],
            )],
            vpc_id=vpc['vpcId'],
            tags = {"Name":f"{group['groupName']}"},
            opts=pulumi.ResourceOptions(provider=awsRegion)
        )
        secGroupIds.update({f"{group['groupName']}-{Region}" : secGroup.id})
    return secGroupIds    




# Create five EC2 instances
def build_instances(instances, vpcData, region, amiId, ssmProfile, secGroupIds, vpc): 

    for instance in instances['instances']:

        # secGroup = aws.ec2.get_security_group(
        #     filters=[
        #         aws.ec2.GetSecurityGroupFilterArgs(
        #             name="tag:Name",
        #             values=[f"{instance['instanceName']}"],
        #         )],
        #     opts=pulumi.InvokeOptions(provider=region))
        
        instance = aws.ec2.Instance(f"{instance['instanceName']}-{vpcData['vpcRegion']}",
            ami=amiId,
            instance_type=instance['size'],
             vpc_security_group_ids=[secGroupIds[f"{instance['instanceName']}-{vpcData['vpcRegion']}"]],
            tags={
                "Name": f"{instance['instanceName']}-{vpcData['vpcRegion']}",
            }|instance['tags'],
            iam_instance_profile=ssmProfile.id,
            subnet_id=vpc['privateSubnet1'],
            # disable_api_termination = True,
            user_data="""#!/bin/bash
            sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
            sudo systemctl enable amazon-ssm-agent
            sudo systemctl start amazon-ssm-agent""",
            opts=pulumi.ResourceOptions(provider=region)
        )