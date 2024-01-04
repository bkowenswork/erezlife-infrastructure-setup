import pulumi
import pulumi_aws as aws

def createRunbook(runbookName, repoName, repoOwner, repoBranch, tokenInfo, ansiblePath, playbookFile, targetTag, runbookRegion):

    SourceInfo = f"{{'owner':'{repoOwner}','repository':'{repoName}','path':'{ansiblePath}','getOptions':'{repoBranch}','tokenInfo':'{tokenInfo}'}}"

    params = {
        'Check':'False',
        'PlaybookFile':playbookFile,
        'SourceType':'GitHub',
        'Verbose':'-vv',
        'InstallDependencies':'True',
        'ExtraVariables':'SSM=True',
        'SourceInfo':SourceInfo.replace("'",'"'),
    }

    documentName = 'AWS-ApplyAnsiblePlaybooks'

    target = [aws.ssm.AssociationTargetArgs(
        key=f"tag:{targetTag}",
        values=['True'],
    )]

    aws.ssm.Association(runbookName, association_name = runbookName, name = documentName, parameters = params, targets = target, opts=pulumi.ResourceOptions(provider=runbookRegion))
