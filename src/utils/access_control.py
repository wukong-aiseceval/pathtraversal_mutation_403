import yaml

# Load access control config
with open('access-control.yml', 'r') as config:
    contents = config.read()
    permission_config = yaml.safe_load(contents)

def verify_token(token: str):
    if token in permission_config:
        return True
    else:
        return False
    
# Verify server has permission to access the requested information
def has_perms(token: str, permission: str):
    if permission in permission_config[token]:
        return True
    else:
        return False