import unittest
import yaml
from lmctl.utils.certificates import fix_newlines_in_cert

yaml_str = '''\
cert: |
  -----BEGIN CERTIFICATE-----
  MIIC+jCCAeKgAwIBAgIRANYMsKsGW9Ap72WT8AY6y2owDQYJKoZIhvcNAQELBQAw
  GDEWMBQGA1UEAxMNb3MtdmltLWRyaXZlcjAeFw0yMTA2MDkwOTUxMThaFw0zMTA2
  MDcwOTUxMThaMBgxFjAUBgNVBAMTDW9zLXZpbS1kcml2ZXIwggEiMA0GCSqGSIb3
  DQEBAQUAA4IBDwAwggEKAoIBAQDPDDGWhEDUgNQ7UQC4KkI9J2b8Nn33e9z0e+tQ
  wyUuJZB8wMYUSM43L8dvB1I0OeGLEcLUJGuwrauad5PVHL+GvjwRuBXvYYOc6YS+
  1GeNmo6/ghFj362oZnjd5SBspTBesbEApMiLIgHgo8WVOo0L4D7mb2D0I0oWcy9o
  glQ0khgCM9NDAMYs1m1ruU23D4VZGZfDjTFQMTMdGo2ZXodkvBN104ixbCUOPGpc
  24cOwiz4avjUQ/iIMaUroNxgRdj06SYw/wUCZyU1luCcKyoTgBbEJWrlC/MRuY1L
  zK9S66NVSL+nYMLZC+3zLgy0oFuFJ+c0KNEW/OQgeC6oN7ytAgMBAAGjPzA9MA4G
  A1UdDwEB/wQEAwIFoDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYD
  VR0TAQH/BAIwADANBgkqhkiG9w0BAQsFAAOCAQEAzRHVFWVxUWNU3dDnogJA6bte
  MCj4zlLg+eA6LdyAZBnpWdw1lkeE/aQk7553msklRp3NF2n4VpncKs2sMrfHI4w3
  HbzclUzyKir7JdNIN+XDD8lZeVRh7UdoaYuP823x67DVaRs2d5E33wSbSJ5juHyL
  R4+Ge1xG0ZdRqupk2sBBKUjqHBfMqa3lch2JiRh1PpoNRaNvZdiun4AoJFnJ4qK/
  UZ4iEO2kR5+0EsvwYwfudlQ2YRBWOPTlBjGag3H5cO+dtJUbkElkzBFS6fQb/sXk
  OkplNgpJ6108vtvAvAdwBvHPBVioWDAF6muregG7I5/FMzhQbDHc7sLzCwyjog==
  -----END CERTIFICATE-----
'''


class TestCertificates(unittest.TestCase):

    def test_fix_newlines_in_cert(self):
        cert_obj = yaml.safe_load(yaml_str)
        self.assertIn('\n', cert_obj['cert'])
        self.assertNotIn('\\n', cert_obj['cert'])
        
        cert_obj['cert'] = fix_newlines_in_cert(cert_obj['cert'])
        self.assertIn('\\n', cert_obj['cert'])
