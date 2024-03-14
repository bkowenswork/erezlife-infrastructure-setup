import pulumi
import ssm
import pulumi_aws as aws

# Create five EC2 instances
def build_instances(databases, vpcData, region, dbSecGroupId, vpc): 
    # regionName = aws.get_region(opts=pulumi.InvokeOptions(provider=region))
    rdsInstances = []

    for database in databases['databases']:
        if database['region'] == vpcData['vpcRegion']:

            # ssm.AddIdToSSM(f"{database['rdsName']}", f"/paramkeys/{database['rdsName']}",f"{database['password']}", databases['ec2Tags'], f"{vpcData['vpcRegion']}") <--- Failed to create 'str' object has no attribute 'package'

            dbSubnetGroup = aws.rds.SubnetGroup(f"{vpcData['vpcEnvironment']}-{database['region']}-{database['rdsName']}".lower(),  
                            subnet_ids=[ vpc['privateSubnet1'],vpc['privateSubnet2']],
                            tags={
                                "Name": f"{vpcData['vpcEnvironment']}-{database['region']}".lower(),
                            })

            rdsInstance = aws.rds.Instance(database['rdsName'],
                allocated_storage=database['storage'],
                db_name=database['default_db'],
                engine=database['engine'],
                engine_version=database['engine_version'],
                instance_class="db.t3.medium",
                # parameter_group_name="default.postgresql13",
                password=database['password'],
                skip_final_snapshot=True,
                publicly_accessible=True,
                db_subnet_group_name=dbSubnetGroup.id,
                vpc_security_group_ids=[dbSecGroupId[f"DB Server-{vpcData['vpcRegion']}"]],
                username="foo",
                opts=pulumi.ResourceOptions(provider=region))
            
            rdsInstances.append({f"{database['rdsName']}-{database['region']}" : rdsInstance.endpoint})

    return rdsInstances
