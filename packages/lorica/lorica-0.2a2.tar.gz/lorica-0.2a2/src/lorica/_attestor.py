# Copyright (c) 2025 Lorica Cybersecurity, Inc. All rights reserved.
# This software is proprietary and confidential. 
# Unauthorized copying of this file via any means is strictly prohibited.
# Lorica Cybersecurity Inc. support@loricacyber.com, May 2025

from cachetools import TTLCache
import hashlib
import jwt
import json
import requests
import time
from typing import Any, Tuple, Optional, Dict
from urllib.parse import urlparse

# URL path constants
DISCOVER_PATH = "/discover"
TOKEN_PATH = "/token"
SECURITY_POLICY_PATH = "/kbs/v0/resource/default/security-policy/test"

class Attestor:
    """
    Class to perform client-side attestation flow for Lorica AI. Includes
    time-based-expiry caching of attestation token and OHTTP key config using
    URLs.
    """
    def __init__(self, trustee_url) -> None:
        """
        Constructor.
        @param trustee_url: The URL to reach Trustee at for token validation.
        """
        url_cache_size = 5 # number of urls to cache token+keyconfig for
        url_cache_ttl = 60 * 10 # 10 minutes
        self.url_cache = TTLCache(maxsize=url_cache_size, ttl=url_cache_ttl)
        self.trustee_url = trustee_url

    @staticmethod
    def _get_base_url(url: str):
        url = urlparse(url)
        return f"{url.scheme}://{url.netloc}"


    @staticmethod
    def _is_jwt_token_expired(token: str):
        """
        Check if the JWT token provided has expired.
        """
        token_payload = jwt.decode(token, options={"verify_signature": False})
        expiry_time = token_payload.get("exp")
        if expiry_time is None:
            raise RuntimeError("Token does not contain an expiration field!")

        curr_time = int(time.time())
        return curr_time > expiry_time


    @staticmethod
    def _fetch_key_config(deployment_url: str):
        url = f"{deployment_url}{DISCOVER_PATH}"
        response = requests.get(url=url)
        if not response.ok:
            raise RuntimeError(
                f"OHTTP key config fetch failed: {response.status_code} ({response.reason}) {response.text}")
        return bytes.fromhex(response.text.strip())


    @staticmethod
    def _fetch_jwt_token(deployment_url: str):
        """
        Fetch the Attestation JWT Token from the deployment.
        """
        url = f"{deployment_url}{TOKEN_PATH}"
        response = requests.get(url=url)
        if not response.ok:
            raise RuntimeError(
                f"Attestation token fetch from deployment failed: "
                f"{response.status_code} ({response.reason}) {response.text}")
        return response.text[1:-1]


    def _raise_if_token_invalid(self, token: str):
        """
        Raise error if token is not valid.
        """
        if self._is_jwt_token_expired(token):
            raise RuntimeError(
                    "Attestation token validation failed: token has expired.")

        url = f"{self.trustee_url}{SECURITY_POLICY_PATH}"
        response = requests.get(url=url,
                                headers={"Authorization": f"Bearer {token}"})
        if not response.ok:
            raise RuntimeError(
                f"Attestation token validation failed: "
                f"{response.status_code} ({response.reason}) {response.text}")


    @staticmethod
    def _raise_if_key_token_mismatch(key_config: bytes, token: str):
        """
        Hash key config according to pcr extend mechanism and confirm the value
        is found in the expected PCR in the token. Raise RuntimeError if it is
        not found.
        """
        pcr_num = 13
        key_config_sha = hashlib.sha256(key_config).digest()
        exp_pcr_val = hashlib.sha256(bytes(32) + key_config_sha).hexdigest()
        token_payload = jwt.decode(token, options={"verify_signature": False})
        pcr_val = json.loads(token_payload["tcb-status"])[f"azsnpvtpm.tpm.pcr{pcr_num}"]
        if pcr_val != exp_pcr_val:
            raise RuntimeError(
                    "OHTTP key config does not satisfy attestation report")


    def _run_client_flow_with_cache(
            self, url: str, attest: bool = True) -> Tuple[bytes, Optional[str]]:
        """
        Run the client-side flow for retrieval of the OHTTP Key Config from the
        deployment with the supplied URL, including attestation if attest
        parameter is set to True. `self.url_cache` is used to cache the
        artifacts of the flow and avoid running it for every call to this
        function.
        @param url: The url for the deployment. May contain additional paths,
        only the scheme and netloc is extracted from the url.
        @param attest: Optional param to enable/disable attestation
        and client-side verification. Enabled by default.
        @return Tuple[bytes, Optional[str]]: A tuple containing the OHTTP Key
        Configuration as bytes and JWT attestation token as str. The OHTTP Key
        Configuration follows the encoding defined by the OHTTP RFC9458. The
        JWT token will be None if attest paramater is set to False.
        """
        # check if this deployment url is in cache and if token expired
        base_url = self._get_base_url(url)
        if base_url in self.url_cache:
            key_config, token = self.url_cache.get(base_url)
            if not attest:
                return key_config, token

            if not (token is None or self._is_jwt_token_expired(token)):
                return key_config, token

        # fetch OHTTP key config from CVM
        key_config = self._fetch_key_config(base_url)

        # if attestation is not required, add key config to cache and return
        if not attest:
            self.url_cache[base_url] = (key_config, None)
            return key_config, None

        # fetch token from CVM
        token = self._fetch_jwt_token(base_url)

        # check if token expired and validate it with Trustee
        self._raise_if_token_invalid(token)

        # verify key is tied to token via PCR values
        self._raise_if_key_token_mismatch(key_config, token)

        # add to cache and return
        self.url_cache[base_url] = (key_config, token)
        return key_config, token


    def get_ohttp_key_config(self, url: str, attest: bool = True) -> bytes:
        """
        Get the OHTTP key configuration from the deployment for the given url
        and perform the client-side attestation flow if attest parameter is set
        to True.
        @param url: The url for the deployment. May contain additional paths,
        only the scheme and netloc is extracted from the url.
        @param attest: Optional param to enable/disable attestation
        and verification. Enabled by default.
        @return bytes: the OHTTP Key Configuration as defined by the OHTTP
        RFC9458 key configuration encoding.
        """
        key_config, _ = self._run_client_flow_with_cache(url, attest)
        return key_config


    def get_attestation_token(self, url: str) -> str:
        """
        Get the attestation JWT produced by Trustee for the deployment serving
        this URL. This funtion only returns a JWT if the deployment passes all
        checks performed by Trustee and this client.
        @param url: The url for the deployment. May contain additional paths,
        only the scheme and netloc is extracted from the url.
        @return str: the JWT.
        """
        _, token = self._run_client_flow_with_cache(url, attest=True)
        return token


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
        token = self.get_attestation_token(url)
        token_payload = jwt.decode(token, options={"verify_signature": False})
        return json.loads(token_payload["tcb-status"])






