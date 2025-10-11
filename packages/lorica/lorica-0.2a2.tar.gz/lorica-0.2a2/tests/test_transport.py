import unittest
from unittest.mock import patch, MagicMock
import httpx
from lorica.transport import Transport
import ohttpy

class TestTransport(unittest.TestCase):
    def setUp(self):
        self.test_url = "https://some.dep.lorica.ai/v1"
        self.key_config = b"test_key_config"
        self.valid_token = "test_token"

    @patch('lorica.transport.Attestor')
    def test_init(self, mock_attestor):
        """Test Transport initialization"""
        default_trustee_url = "https://trustee.lorica.ai"

        # Test with default parameters
        transport = Transport()
        self.assertEqual(transport.trustee_url, default_trustee_url)
        self.assertTrue(transport.attest)
        mock_attestor.assert_called_once_with(default_trustee_url)

        # Test with custom trustee param
        custom_trustee_url = "https://custom.trustee.com"
        transport = Transport(
            trustee_url=custom_trustee_url)
        self.assertEqual(transport.trustee_url, custom_trustee_url)
        self.assertTrue(transport.attest)
        mock_attestor.assert_called_with(custom_trustee_url)

        # Test with custom attest param
        transport = Transport(attest=False)
        self.assertEqual(transport.trustee_url, default_trustee_url)
        self.assertFalse(transport.attest)


    @patch('lorica.transport.Attestor')
    def test_handle_request(self, mock_attestor):
        """Test handle_request method"""
        # Setup mocks
        mock_attestor_instance = mock_attestor.return_value
        mock_attestor_instance.get_ohttp_key_config.return_value = self.key_config
        
        # Create transport and mock parent class handle_request method
        transport = Transport()
        with patch.object(
                httpx.BaseTransport, 'handle_request', return_value=MagicMock()
            ), patch.object(
                 ohttpy.Transport, 'handle_request', return_value=MagicMock()
            ) as mock_parent_handle:
            
            # Create a test request
            request = httpx.Request("GET", self.test_url)
            
            # Call handle_request
            transport.handle_request(request)
            
            # Verify attestor was called correctly
            mock_attestor_instance.get_ohttp_key_config.assert_called_once_with(
                self.test_url, attest=True)
            
            # Verify parent class handle_request was called
            mock_parent_handle.assert_called_once()
            
            # Verify key_config was set
            self.assertEqual(transport.key_config, self.key_config)

    @patch('lorica.transport.Attestor')
    def test_get_attestation_token(self, mock_attestor):
        """Test get_attestation_token method"""
        # Setup mocks
        mock_attestor_instance = mock_attestor.return_value
        mock_attestor_instance.get_attestation_token.return_value = self.valid_token
        
        # Create transport and call method
        transport = Transport()
        result = transport.get_attestation_token(self.test_url)
        
        # Verify result and attestor was called correctly
        self.assertEqual(result, self.valid_token)
        mock_attestor_instance.get_attestation_token.assert_called_once_with(
            self.test_url)

    @patch('lorica.transport.Attestor')
    def test_get_attested_deployment_report(self, mock_attestor):
        """Test get_attested_deployment_report method"""
        # Setup mocks
        mock_attestor_instance = mock_attestor.return_value
        mock_report = {"tcb-status": "test_status"}
        mock_attestor_instance.get_attested_deployment_report.return_value = mock_report
        
        # Create transport and call method
        transport = Transport()
        result = transport.get_attested_deployment_report(self.test_url)
        
        # Verify result and attestor was called correctly
        self.assertEqual(result, mock_report)
        mock_attestor_instance.get_attested_deployment_report.assert_called_once_with(
            self.test_url)

if __name__ == '__main__':
    unittest.main() 