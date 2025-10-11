import hashlib
import unittest
from unittest.mock import patch, MagicMock
import jwt
import time
import json
from lorica._attestor import Attestor, DISCOVER_PATH, TOKEN_PATH, SECURITY_POLICY_PATH
import random
import string

class TestAttestor(unittest.TestCase):
    def simulate_empty_pcr_extend(self, data: bytes) -> bytes:
        """
        Simulate extending an empty pcr with provided data. (empty pcr is one with zero-ed value).
        """
        data_sha = hashlib.sha256(data).digest()
        return hashlib.sha256(bytes(32) + data_sha).digest()
    
    def _get_mock_get_side_effect(self, key_config, token):
        """Helper method to create mock_get side effect for testing"""
        mock_discover_response = MagicMock()
        mock_discover_response.ok = True
        mock_discover_response.text = key_config.hex()
        
        mock_token_response = MagicMock()
        mock_token_response.ok = True
        mock_token_response.text = f'"{token}"'
        
        mock_trustee_response = MagicMock()
        mock_trustee_response.ok = True
        
        def side_effect(url, **kwargs):
            if url.endswith(DISCOVER_PATH):
                return mock_discover_response
            elif url.endswith(TOKEN_PATH):
                return mock_token_response
            elif url.endswith(SECURITY_POLICY_PATH):
                return mock_trustee_response
            return MagicMock(ok=False)
        
        return side_effect

    def setUp(self):
        self.trustee_url = "https://trustee.lorica.ai"
        self.attestor = Attestor(self.trustee_url)
        self.test_url = "https://example.com/api/v1"
        self.test_base_url = "https://example.com"

        # Sample key config
        self.key_config = b"test_key_config"
        
        # Sample JWT token payload
        self.token_payload = {
            "exp": int(time.time()) + 3600,  # 1 hour from now
            "tcb-status": json.dumps({
                "azsnpvtpm.tpm.pcr13": self.simulate_empty_pcr_extend(self.key_config).hex()
            })
        }
        self.valid_token = jwt.encode(
            self.token_payload, "secret", algorithm="HS256"
        )

    def test_get_base_url(self):
        """Test _get_base_url static method"""
        # Test multiple random URLs
        for _ in range(10):
            domain = ''.join(random.choices(string.ascii_lowercase, k=8)) + '.com'
            path = ('/' + ''.join(random.choices(string.ascii_lowercase, k=5)) 
                   if random.random() < 0.3 else "")
            port = f":{random.randint(1000, 9999)}" if random.random() < 0.3 else ""
            scheme = random.choice(['http', 'https'])
            
            input_url = f"{scheme}://{domain}{port}{path}"
            expected_base = f"{scheme}://{domain}{port}"
            
            with self.subTest(input_url=input_url):
                self.assertEqual(
                    Attestor._get_base_url(input_url), expected_base)

    def test_is_jwt_token_expired(self):
        """Test JWT token expiration check"""
        # Test valid token
        self.assertFalse(Attestor._is_jwt_token_expired(self.valid_token))
        
        # Test expired token
        expired_payload = self.token_payload.copy()
        expired_payload["exp"] = int(time.time()) - 3600  # 1 hour ago
        expired_token = jwt.encode(
            expired_payload, "secret", algorithm="HS256")
        self.assertTrue(Attestor._is_jwt_token_expired(expired_token))
        
        # Test token without exp field
        invalid_payload = {"some_field": "value"}
        invalid_token = jwt.encode(
            invalid_payload, "secret", algorithm="HS256")
        with self.assertRaises(RuntimeError):
            Attestor._is_jwt_token_expired(invalid_token)

    @patch('requests.get')
    def test_fetch_key_config(self, mock_get):
        """Test fetching key config from deployment"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = "0123456789abcdef"  # Valid hex string
        mock_get.return_value = mock_response

        result = Attestor._fetch_key_config(self.test_base_url)
        self.assertEqual(result, bytes.fromhex("0123456789abcdef"))
        mock_get.assert_called_once_with(
            url=f"{self.test_base_url}{DISCOVER_PATH}")

        # Test error case
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.text = "Error message"
        with self.assertRaises(RuntimeError):
            Attestor._fetch_key_config(self.test_base_url)

    @patch('requests.get')
    def test_fetch_jwt_token(self, mock_get):
        """Test fetching JWT token from deployment"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = f'"{self.valid_token}"'
        mock_get.return_value = mock_response

        result = Attestor._fetch_jwt_token(self.test_base_url)
        self.assertEqual(result, self.valid_token)
        mock_get.assert_called_once_with(
            url=f"{self.test_base_url}{TOKEN_PATH}")

        # Test error case
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.text = "Error message"
        with self.assertRaises(RuntimeError):
            Attestor._fetch_jwt_token(self.test_base_url)

    @patch('requests.get')
    def test_raise_if_token_invalid(self, mock_get):
        """Test token validation with Trustee"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_get.return_value = mock_response

        # Test valid token
        self.attestor._raise_if_token_invalid(self.valid_token)
        mock_get.assert_called_once_with(
            url=(f"{self.trustee_url}{SECURITY_POLICY_PATH}"),
            headers={"Authorization": f"Bearer {self.valid_token}"})

        # Test expired token
        expired_payload = self.token_payload.copy()
        expired_payload["exp"] = int(time.time()) - 3600
        expired_token = jwt.encode(
            expired_payload, "secret", algorithm="HS256")
        with self.assertRaises(RuntimeError):
            self.attestor._raise_if_token_invalid(expired_token)

        # Test invalid token response
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.reason = "Unauthorized"
        mock_response.text = "Invalid token"
        with self.assertRaises(RuntimeError):
            self.attestor._raise_if_token_invalid(self.valid_token)

    def test_raise_if_key_token_mismatch(self):
        """Test key config and token PCR value matching"""
        # Test success case - using existing compatible key_config and valid_token
        Attestor._raise_if_key_token_mismatch(self.key_config, self.valid_token)
        
        # Test failure case - mismatched key config and token
        different_key_config = b"different_key_config"
        with self.assertRaises(RuntimeError) as context:
            Attestor._raise_if_key_token_mismatch(different_key_config, self.valid_token)
        self.assertIn("OHTTP key config does not satisfy attestation report", 
                     str(context.exception))

    @patch('requests.get')
    def test_run_client_flow_with_cache(self, mock_get):
        """Test client flow with caching"""
        mock_get.side_effect = self._get_mock_get_side_effect(
            self.key_config, self.valid_token)

        # Test first call (not cached)
        key_config, token = self.attestor._run_client_flow_with_cache(
            self.test_url)
        self.assertEqual(key_config, self.key_config)
        self.assertEqual(token, self.valid_token)
        
        # Test cached call
        key_config, token = self.attestor._run_client_flow_with_cache(
            self.test_url)
        self.assertEqual(key_config, self.key_config)
        self.assertEqual(token, self.valid_token)
        
        # Verify requests were made correctly
        self.assertEqual(mock_get.call_count, 3)  # discover, token, trustee
        mock_get.assert_any_call(url=f"{self.test_base_url}{DISCOVER_PATH}")
        mock_get.assert_any_call(url=f"{self.test_base_url}{TOKEN_PATH}")
        mock_get.assert_any_call(
            url=f"{self.trustee_url}{SECURITY_POLICY_PATH}",
            headers={"Authorization": f"Bearer {self.valid_token}"})

    @patch('requests.get')
    def test_get_ohttp_key_config_without_attest(self, mock_get):
        """Test getting OHTTP key config without attest"""
        mock_get.side_effect = self._get_mock_get_side_effect(
            self.key_config, self.valid_token)
        
        result = self.attestor.get_ohttp_key_config(self.test_url, attest=False)
        self.assertEqual(result, self.key_config)

        # Verify requests were made correctly
        self.assertEqual(mock_get.call_count, 1)
        mock_get.assert_any_call(url=f"{self.test_base_url}{DISCOVER_PATH}")

    @patch('requests.get')
    def test_get_ohttp_key_config_with_attest(self, mock_get):
        """Test getting OHTTP key config with attest"""
        mock_get.side_effect = self._get_mock_get_side_effect(
            self.key_config, self.valid_token)
        result = self.attestor.get_ohttp_key_config(self.test_url, attest=True)
        self.assertEqual(result, self.key_config)
        
        # Verify requests were made correctly
        self.assertEqual(mock_get.call_count, 3)  # discover, token, trustee
        mock_get.assert_any_call(url=f"{self.test_base_url}{DISCOVER_PATH}")
        mock_get.assert_any_call(url=f"{self.test_base_url}{TOKEN_PATH}")
        mock_get.assert_any_call(
            url=f"{self.trustee_url}{SECURITY_POLICY_PATH}",
            headers={"Authorization": f"Bearer {self.valid_token}"})

    @patch('requests.get')
    def test_get_attestation_token(self, mock_get):
        """Test getting attestation token"""
        mock_get.side_effect = self._get_mock_get_side_effect(
            self.key_config, self.valid_token)
        
        result = self.attestor.get_attestation_token(self.test_url)
        self.assertEqual(result, self.valid_token)
        
        # Verify requests were made correctly
        self.assertEqual(mock_get.call_count, 3)  # discover, token, trustee
        mock_get.assert_any_call(url=f"{self.test_base_url}{DISCOVER_PATH}")
        mock_get.assert_any_call(url=f"{self.test_base_url}{TOKEN_PATH}")
        mock_get.assert_any_call(
            url=f"{self.trustee_url}{SECURITY_POLICY_PATH}",
            headers={"Authorization": f"Bearer {self.valid_token}"})

    @patch('requests.get')
    def test_get_attested_deployment_report(self, mock_get):
        """Test getting attested deployment report"""
        mock_get.side_effect = self._get_mock_get_side_effect(
            self.key_config, self.valid_token)
        
        result = self.attestor.get_attested_deployment_report(self.test_url)
        self.assertEqual(result, json.loads(self.token_payload["tcb-status"]))
        
        # Verify requests were made correctly
        self.assertEqual(mock_get.call_count, 3)  # discover, token, trustee
        mock_get.assert_any_call(url=f"{self.test_base_url}{DISCOVER_PATH}")
        mock_get.assert_any_call(url=f"{self.test_base_url}{TOKEN_PATH}")
        mock_get.assert_any_call(
            url=f"{self.trustee_url}{SECURITY_POLICY_PATH}",
            headers={"Authorization": f"Bearer {self.valid_token}"})

if __name__ == '__main__':
    unittest.main() 