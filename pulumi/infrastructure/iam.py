import json
import pulumi_aws as aws

# Create an instance role
def create_ssm_role():
    ec2_role = aws.iam.Role(
        "instance-profile-role",
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
        ,
        name="managed-instance-role",
        tags={'Name': 'managed-instance-role'}
    )

    aws.iam.RolePolicyAttachment(
        "ssm-role-policy-attachment",
        aws.iam.RolePolicyAttachmentArgs(
            role=ec2_role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
        ),
    )

    aws.iam.RolePolicyAttachment(
        "s3-role-policy-attachment",
        aws.iam.RolePolicyAttachmentArgs(
            role=ec2_role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        ),
    )

    aws.iam.RolePolicyAttachment(
        "paramstore-role-policy-attachment",
        aws.iam.RolePolicyAttachmentArgs(
            role=ec2_role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonSSMFullAccess"
        ),
    )

    return aws.iam.InstanceProfile("managedEC2Profile", role=ec2_role.name)