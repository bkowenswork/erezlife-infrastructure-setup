import random
import string
import ssm


def create_keys(paramKeys, region):
    for param in paramKeys['paramkeys']:
        ssm.AddIdToSSM(param['name'], "/paramkeys/"+param['name'], token(param['size']), paramKeys['paramkeyTags'], region)
    
def token(length):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))