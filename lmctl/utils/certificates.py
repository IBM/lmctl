import re

# Replace \n but not \\n
new_line_pattern = re.compile('((?<!\\\)\n)+')

def read_certificate_file(path):
    with open(path, 'rt') as f:
        certificate = f.read()
        certificate = certificate.replace("\n", "\\n")
        return certificate

def fix_newlines_in_cert(cert_value_str):
    """
    Replaces "\n" with "\\n" so new lines are maintained when sent to Brent (Resource Manager)
    """
    cert_value_str = re.sub(new_line_pattern, '\\\\n', cert_value_str) # 4 "\\\\" to create "\\" as slashes need escaping
    return cert_value_str