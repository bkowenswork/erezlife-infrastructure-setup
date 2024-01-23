import pulumi
import pulumi_aws as aws

def generate_ssm(filepath, filestring, prefix):
    aws.ssm.Parameter(filepath, type="String", name=prefix+filepath, value=filestring, opts=pulumi.ResourceOptions(provider=awseast2))


# /STACK/ENVIRONMENT/REGION/RESOURCE/NAME
    
def AddIdToSSM(resource, name, value, tags, region):
    ssmParameter = ""
    pulumi.log.info(f'Checking for Parameter: {name}')
    try:
        ssmParameter = aws.ssm.Parameter(resource,
            description="The parameter description",
            type="SecureString",
            name=name,
            value=value,
            tags=tags,
            opts=pulumi.ResourceOptions(provider=region))
    except Exception as e:
        raise pulumi.RunError(f"Failed to create {str(e)}") 
        # pulumi.log.info(f'code: {error}')
        # if error == 'ParameterNotFound':
        #     pulumi.log.error(f'SSM Parameter not found: {name}')
        # else:
        #     # Handle other potential errors.
        #     pulumi.log.error(error.__str__())

    if ssmParameter == "":
        ssmParameter = aws.ssm.get_parameter(name=name, opts=pulumi.InvokeOptions(provider=region))   

    return ssmParameter    

def GetIdFromSSM(name, region):
    return aws.ssm.get_parameter(name=name, opts=pulumi.InvokeOptions(provider=region)).value