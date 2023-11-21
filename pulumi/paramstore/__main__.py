import utils
import ssm
import pulumi_aws as aws

## Process inventory files

inventory = utils.read_import_list("./files/inventory.yaml")
for item in inventory['param-files']:
    ssm.generate_ssm(item['filepath'], utils.readfile_to_var(item['filename']), "/erezlife/jenkins")