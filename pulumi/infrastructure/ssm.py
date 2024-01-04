import pulumi
import pulumi_aws as aws


awseast2 = aws.Provider('aws-east-2', region='us-east-2')

def generate_ssm(filepath, filestring, prefix):
    aws.ssm.Parameter(filepath, type="String", name=prefix+filepath, value=filestring, opts=pulumi.ResourceOptions(provider=awseast2))
