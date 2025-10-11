# Copyright (c) 2025 Lorica Cybersecurity, Inc. All rights reserved.
# This software is proprietary and confidential. 
# Unauthorized copying of this file via any means is strictly prohibited.
# Lorica Cybersecurity Inc. support@loricacyber.com, May 2025

import httpx
import ohttpy
from lorica._attestor import Attestor
from typing import Dict

class Transport(ohttpy.Transport):
    """
    Class to serve as a drop-in replacement from httpx.BaseTransport while
    enabling attestation and OHTTP encapsulation for all HTTP communication.
    @param key_config Optional bytes parameter to provide the OHTTP key
    configuration as defined by the OHTTP RFC9458 key configuration encoding.
    This contains the OHTTP public key and set of algorithms for HPKE context.
    If not provided, the key config will be fetched dynamically from
    `{url.scheme}://{url.authority}/discover` endpoint for the url specified in
    an HTTP request.
    """
    def __init__(self,
                 trustee_url: str = "https://trustee.lorica.ai",
                 attest: bool = True) -> None:
        """
        Constructor.
        @param trustee_url: The URL to reach Trustee at for token validation,
        defaults to reaching Lorica's Trustee.
        @param attest: True if validation of token and key configuration should
        be performed.
         """
        super().__init__()
        self.trustee_url = trustee_url
        self.attest = attest
        self.attestor = Attestor(self.trustee_url)


    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """
        Use self.attestor to retrieve OHTTP key config and perform attestation
        flow. Use base class to send OHTTP-wrapped request.
        For interface, see @httpx.BaseTransport.handle_request().
        """
        key_config = self.attestor.get_ohttp_key_config(
                str(request.url), attest=self.attest)
        self.key_config = key_config # provide parent with key_config
        return super().handle_request(request)


    def get_attestation_token(self, url: str) -> str:
        """
        Get the attestation JWT produced by Trustee for the deployment serving
        this URL. This funtion only returns a JWT if the deployment passes all
        checks performed by Trustee and this client.
        @param url: The url for the deployment. May contain additional paths,
        only the scheme and netloc is extracted from the url.
        @return str: the JWT.
        """
        return self.attestor.get_attestation_token(url)


    def get_attested_deployment_report(self, url: str) -> Dict[str, str]:
        """
        Get the attestation report for the deployment serving this URL. This
        report is generated as part of the client-side attestation flow. This
        funtion only returns a report if the deployment passes all checks
        performed by Trustee and this client.
        @param url: The url for the deployment. May contain additional paths,
        only the scheme and netloc is extracted from the url.
        @return dict[str, str]: the report.
        """
        return self.attestor.get_attested_deployment_report(url)

