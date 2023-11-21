import yaml

def readfile_to_var(filepath):
    with open(filepath, 'r') as file:
        return file.read().rstrip()
    
def read_import_list(listfile):
    with open(listfile) as file:
        try:
            return yaml.safe_load(file)   
        except yaml.YAMLError as exc:
            print(exc)

             