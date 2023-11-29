import pulumi
import pulumi_aws as aws


awseast2 = aws.Provider('aws-east-2', region='us-east-2')

def createRunbook(runbookName):

    SourceInfo = '''{"owner":"bkowenswork","repository":"ansible-server-setup","path":".","getOptions":"branch:INFRA-18","tokenInfo":"{{ssm-secure:/bkowens-github-token}}"}'''

    params = {
        "Check":"False",
        "PlaybookFile":"jenkins.yml",
        "SourceType":"GitHub",
        "Verbose":"-vv",
        "InstallDependencies":"True",
        "ExtraVariables":"SSM=True",
        "SourceInfo":SourceInfo,
    }

    documentName = "AWS-ApplyAnsiblePlaybooks"

    target = [aws.ssm.AssociationTargetArgs(
        key="tag:ssm-jenkins-ansible",
        values=["True"],
    )]

    aws.ssm.Association(runbookName, association_name = runbookName, name = documentName, parameters = params, targets = target, opts=pulumi.ResourceOptions(provider=awseast2) )