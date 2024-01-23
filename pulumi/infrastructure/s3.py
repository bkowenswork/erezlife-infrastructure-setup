import pulumi_aws as aws

def create_bucket(s3Config):
    for bucket in s3Config['buckets']:
        aws.s3.Bucket(f"{s3Config['stackName']}-{s3Config['envName']}-{bucket['name']}",
            acl=bucket['acl'],
            bucket=f"{s3Config['stackName']}-{s3Config['envName']}-{bucket['name']}",
            tags=s3Config['s3Tags']
            )    
                