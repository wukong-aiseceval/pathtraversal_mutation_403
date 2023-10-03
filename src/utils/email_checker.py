import re
import socket

def is_valid_email(email):
    # Basic format check
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    
    # Split email into local part and domain part
    local_part, domain = email.split("@")
    
    # DNS MX record check
    try:
        mx_records = socket.getaddrinfo(domain, None, socket.AF_INET, socket.SOCK_STREAM)
        if not any([record[1] == socket.SOCK_STREAM for record in mx_records]):
            return False
    except socket.gaierror:
        return False
    
    return True