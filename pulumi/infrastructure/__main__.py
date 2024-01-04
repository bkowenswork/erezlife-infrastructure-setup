import runbook
import utils
import vpc
import pulumi
import pulumi_aws as aws

awseast2 = aws.Provider('aws-east-2', region='us-east-2')
awseast1 = aws.Provider('aws-east-1', region='us-east-1')
cacentral1 = aws.Provider('aws-central-1', region='ca-central-1')


usConfig = utils.read_config("./files/prod-useast1.yaml")
caConfig = utils.read_config("./files/prod-cacentral1.yaml") 

vpc.create_vpc(usConfig, awseast1)
vpc.create_vpc(caConfig, cacentral1)

stackname = pulumi.get_stack()

usVpcID = pulumi.StackReference(stackname).get_output(f"{usConfig['vpcName']}-vpcid")
caVpcID = pulumi.StackReference(stackname).get_output(f"{caConfig['vpcName']}-vpcid")

runBooks = utils.read_config("./files/runbooks.yaml") 

for association in runBooks['associations']:
    runbook.createRunbook(runbookName, repoName, repoOwner, repoBranch, tokenInfo, ansiblePath, playbookFile, targetTag)
    association['']

