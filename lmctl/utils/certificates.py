def read_certificate_file(path):
    with open(path, 'rt') as f:
        certificate = f.read()
        certificate = certificate.replace("\n", "\\n")
        return certificate