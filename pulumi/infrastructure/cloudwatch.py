import pulumi
import ssm
import pulumi_aws as aws


def create_group(vpcData, vpcRegion):

    log_group = aws.cloudwatch.LogGroup(
    f"{vpcData['vpcAccount']}-{vpcData['vpcRegionPrefix']}-{vpcData['vpcAppShortname']}",
    name=f"/{vpcData['vpcAccount']}-{vpcData['vpcRegionPrefix']}-{vpcData['vpcAppShortname']}",
    tags=vpcData['vpcTags'])

    ssm.AddIdToSSM(
        f"{vpcData['vpcRegionPrefix']}-{vpcData['vpcAppShortname']}-loggroup", 
        f"{vpcData['vpcAppShortname']}-loggroup", 
        f"/{vpcData['vpcAccount']}-{vpcData['vpcRegionPrefix']}-{vpcData['vpcAppShortname']}",
        vpcData['vpcTags'], 
        vpcRegion)   

    # Export the name of the log group
    pulumi.export(f"{vpcData['vpcAccount']}-{vpcData['vpcRegionPrefix']}-{vpcData['vpcAppShortname']}", log_group.name)
