import pulumi
import pulumi_aws as aws

def create_sg(sgData,awsRegion, Region, vpc):
    secGroupIds = {}
    for group in sgData['groups']:
        ingressSet = []
        for rule in group['rules']:  
            ingressSet.append(aws.ec2.SecurityGroupIngressArgs( protocol=rule['protocol'], from_port=rule['from_port'], to_port=rule['to_port'], cidr_blocks=[rule['cidr']]))

        secGroup = aws.ec2.SecurityGroup(f"{group['groupName']}-{Region}",
            ingress=ingressSet,
            vpc_id=vpc.id,
            tags = {"Name":f"{group['groupName']}"},
            opts=pulumi.ResourceOptions(provider=awsRegion, depends_on=[vpc])
        )
        secGroupIds.update({f"{group['groupName']}-{Region}" : secGroup.id})
    return secGroupIds    




# Create five EC2 instances
def build_instances(instances, region, amiId, Region, ssmProfile, subnet, secGroupIds):    
    for instance in instances['instances']:

        # secGroup = aws.ec2.get_security_group(
        #     filters=[
        #         aws.ec2.GetSecurityGroupFilterArgs(
        #             name="tag:Name",
        #             values=[f"{instance['instanceName']}"],
        #         )],
        #     opts=pulumi.InvokeOptions(provider=region))
        
        instance = aws.ec2.Instance(f"{instance['instanceName']}-{Region}",
            ami=amiId,
            instance_type=instance['size'],
             vpc_security_group_ids=[secGroupIds[f"{instance['instanceName']}-{Region}"]],
            tags={
                "Name": f"{instance['instanceName']}-{Region}",
            },
            iam_instance_profile=ssmProfile.id,
            subnet_id=subnet.id,
            disable_api_termination = True,
            user_data="""#!/bin/bash
            sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
            sudo systemctl enable amazon-ssm-agent
            sudo systemctl start amazon-ssm-agent""",
            opts=pulumi.ResourceOptions(provider=region)
        )