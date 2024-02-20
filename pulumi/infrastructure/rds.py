import pulumi
import ssm
import pulumi_aws as aws

# Create five EC2 instances
def build_instances(databases, vpcData, region, dbSecGroupId): 

    subnet1id = ssm.GetIdFromSSM(f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/subnets/private1", region)
    subnet2id = ssm.GetIdFromSSM(f"/sandbox/{vpcData['vpcEnvironment']}/{vpcData['vpcRegion']}/{vpcData['vpcName']}/subnets/private2", region)
    # regionName = aws.get_region(opts=pulumi.InvokeOptions(provider=region))
    rdsInstances = []

    for database in databases['databases']:
        if database['region'] == vpcData['vpcRegion']:

            dbSubnetGroup = aws.rds.SubnetGroup(f"{vpcData['vpcEnvironment']}-{database['region']}-{database['rdsName']}".lower(),  
                            subnet_ids=[ subnet1id,subnet2id],
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
                password="foobarbaz",
                skip_final_snapshot=True,
                publicly_accessible=True,
                db_subnet_group_name=dbSubnetGroup.id,
                vpc_security_group_ids=[dbSecGroupId[f"DB Server-{vpcData['vpcRegion']}"]],
                username="foo",
                opts=pulumi.ResourceOptions(provider=region))
            
            rdsInstances.append({f"{database['rdsName']}-{database['region']}" : rdsInstance.endpoint})

    return rdsInstances
