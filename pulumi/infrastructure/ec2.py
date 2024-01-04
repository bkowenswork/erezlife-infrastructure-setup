import pulumi
import pulumi_aws as aws

def create_sg(sgData,awsRegion):

    for group in sgData['groups']:

        aws.ec2.SecurityGroup(f"{sgData['groupName']}",
            ingress=[ingresses(group['rules'])],
            tags = sgData['sgTags']|{"Name":f"{group['groupName']}"},
            opts=pulumi.ResourceOptions(provider=awsRegion)
        )

def ingresses(rules):
    ingresses = []
    for rule in rules:                
        ingresses.append(aws.ec2.SecurityGroupIngressArgs(
            protocol=rule['protocol'],
            from_port=rule['from_port'],
            to_port=rule['to_port'],
            cidr_blocks=[rule['cidr']],
        ))
    return ingresses    


# Create an instance role
def create_ssm_role():
    ec2_role = aws.iam.Role(
        "managed-instance-role",
        aws.iam.RoleArgs(
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com",
                    },
                    "Action": "sts:AssumeRole",
                },
            })
        ),
        opts=pulumi.ResourceOptions(
            parent=self
        ),
    )

    aws.iam.RolePolicyAttachment(
        "ssm-role-policy-attachment",
        aws.iam.RolePolicyAttachmentArgs(
            role=ec2_role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
        ),
        opts=pulumi.ResourceOptions(
            parent=self
        ),
    )

    aws.iam.RolePolicyAttachment(
        "s3-role-policy-attachment",
        aws.iam.RolePolicyAttachmentArgs(
            role=ec2_role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        ),
        opts=pulumi.ResourceOptions(
            parent=self
        ),
    )

# Create five EC2 instances
def build_instances(instances, region, amiId):    
    for instance in instances:
        instance = aws.ec2.Instance(f"{instance['instanceName']}",
            ami=amiId,
            instance_type=instance['size'],
            security_groups=[aws.ec2.get_security_group( filters = [ aws.ec2.GetSecurityGroupFilter(name='name', values=[f"{instance['security_group']}"])])],
            tags={
                "Name": f"{instances['instanceName']}"|instance["tags"],
            },
            iam_instance_profile=instance['profile'],
            user_data="""#!/bin/bash
            sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
            sudo systemctl enable amazon-ssm-agent
            sudo systemctl start amazon-ssm-agent""",
        )
