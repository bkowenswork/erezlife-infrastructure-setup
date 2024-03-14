import utils
import vpc
import ec2
import iam
import s3
import paramkeys
import rds
import runbook
import pulumi_aws as aws

# SET UP YOUR REGION PROVIDERS
awseast2 = aws.Provider('aws-east-2', region='us-east-2')
awseast1 = aws.Provider('aws-east-1', region='us-east-1')
cacentral1 = aws.Provider('aws-central-1', region='ca-central-1')

# CREATE YOUR VPC AND RELATED RESOURCES
usConfig = utils.read_config("./files/prod-useast1.yaml")
caConfig = utils.read_config("./files/prod-cacentral1.yaml") 

usVpc = vpc.create_vpc(usConfig, awseast1)
caVpc = vpc.create_vpc(caConfig, cacentral1)

# usSubnet = vpc.create_subnets(usConfig, awseast1)
# caSubnet = vpc.create_subnets(caConfig, cacentral1)

vpc.create_peering(usVpc, caVpc, cacentral1)

# # CREATE THE SECURITY GROUPS
secGroups = utils.read_config("./files/securitygroups.yaml")
usGroupIds = ec2.create_sg(secGroups, awseast1, 'us-east-1', usVpc)
caGroupIds = ec2.create_sg(secGroups, cacentral1, 'ca-central-1', caVpc)

# CREATE THE S3 BUCKETS
S3Config = utils.read_config("./files/prod-S3buckets.yaml")
bucketConfig = s3.create_bucket(S3Config)

# CREATE THE PARAMKEYS
paramConfig = utils.read_config("./files/paramkeys.yaml")
paramkeys.create_keys(paramConfig,awseast1)

# CREATE THE DATABASES
rdsConfig = utils.read_config("./files/prod-databases.yaml")
rds.build_instances(rdsConfig, usConfig, awseast1, usGroupIds, usVpc)
# rds.build_instances(rdsConfig, caConfig, cacentral1, caGroupIds, caVpc)

# CREATE THE EC2 INSTANCES
ssmProfile = iam.create_ssm_role()
instances = utils.read_config("./files/instances.yaml")
ec2.build_instances(instances, usConfig, awseast1, 'ami-079db87dc4c10ac91', ssmProfile, usGroupIds, usVpc)
# ec2.build_instances(instances, cacentral1, 'ami-0fe6c9864169f4e41', 'ca-central-1', ssmProfile, usSubnet, usGroupIds)

runBooks = utils.read_config("./files/runbooks.yaml") 
for association in runBooks['associations']:
    runbook.createRunbook(awseast1, association['name'], association['repoName'], association['repoOwner'], association['repoBranch'], association['tokenInfo'], association['ansiblePath'], association['playbookFile'], association['targetTag'])