# Copyright (c) 2025 Lorica Cybersecurity, Inc. All rights reserved.
# This software is proprietary and confidential. 
# Unauthorized copying of this file via any means is strictly prohibited.
# Lorica Cybersecurity Inc. support@loricacyber.com, May 2025

import json
import ohttpy
import requests
from lorica._attestor import Attestor
from typing import Any, Dict
from urllib.parse import urlparse

class Session(ohttpy.Session):
    """
    Class to serve as a drop-in replacement from request.Session while enabling
    attestation and OHTTP encapsulation for all HTTP communication.
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


    def send(self, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        """
        Use self.attestor to retrieve OHTTP key config and perform attestation
        flow. Use base class to send OHTTP-wrapped request.
        For interface, see @requests.Session.send().
        """
        key_config = self.attestor.get_ohttp_key_config(
                request.url, attest=self.attest)
        self.key_config = key_config # provide parent with key_config
        return super().send(request, **kwargs)


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


