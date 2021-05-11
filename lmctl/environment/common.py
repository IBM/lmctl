from typing import Union

def build_address(host: str, 
                  protocol: str = 'https',
                  port: Union[str, int] = None, 
                  path: str = None):
    port = str(port).strip() if port is not None else None
    protocol = protocol.strip().lower() if protocol is not None else None
    if protocol is None or len(protocol) == 0:
        protocol = 'https'
    path = path.strip() if path is not None else None
    address = protocol
    if not address.endswith('://'):
        address += '://'
    address += host
    if port is not None and len(port) > 0:
        address += f':{port}'
    if path is not None and len(path) > 0:
        if not address.endswith('/'):
            address += '/'
        address += path
    if address.endswith('/'):
        address[:-1]
    return address