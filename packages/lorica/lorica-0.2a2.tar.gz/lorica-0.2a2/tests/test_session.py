import unittest
from unittest.mock import patch, MagicMock
import requests
from lorica.session import Session
from lorica._attestor import Attestor
import ohttpy

class TestSession(unittest.TestCase):
    def setUp(self):
        self.test_url = "https://some.dep.lorica.ai/v1"
        self.key_config = b"test_key_config"
        self.valid_token = "test_token"

    @patch('lorica.session.Attestor')
    def test_init(self, mock_attestor):
        """Test Session initialization"""
        default_trustee_url = "https://trustee.lorica.ai"

        # Test with default parameters
        session = Session()
        self.assertEqual(session.trustee_url, default_trustee_url)
        self.assertTrue(session.attest)
        mock_attestor.assert_called_once_with(default_trustee_url)

        # Test with custom trustee param
        custom_trustee_url = "https://custom.trustee.com"
        session = Session(
            trustee_url=custom_trustee_url)
        self.assertEqual(session.trustee_url, custom_trustee_url)
        self.assertTrue(session.attest)
        mock_attestor.assert_called_with(custom_trustee_url)

        # Test with custom attest param
        session = Session(attest=False)
        self.assertEqual(session.trustee_url, default_trustee_url)
        self.assertFalse(session.attest)

    @patch('lorica.session.Attestor')
    def test_send(self, mock_attestor):
        """Test send method"""
        # Setup mocks
        mock_attestor_instance = mock_attestor.return_value
        mock_attestor_instance.get_ohttp_key_config.return_value = self.key_config
        
        # Create session and mock parent class send method
        session = Session()
        with patch.object(session, 'key_config', None), \
             patch.object(
                 ohttpy.Session, 'send', return_value=MagicMock()
             ) as mock_parent_send:
            
            # Create a test request
            request = requests.PreparedRequest()
            request.url = self.test_url
            
            # Call send
            session.send(request)
            
            # Verify attestor was called correctly
            mock_attestor_instance.get_ohttp_key_config.assert_called_once_with(
                self.test_url, attest=True)
            
            # Verify key_config was set for parent class
            self.assertEqual(session.key_config, self.key_config)
            
            # Verify parent class send was called
            mock_parent_send.assert_called_once()
            

    @patch('lorica.session.Attestor')
    def test_get_attestation_token(self, mock_attestor):
        """Test get_attestation_token method"""
        # Setup mocks
        mock_attestor_instance = mock_attestor.return_value
        mock_attestor_instance.get_attestation_token.return_value = self.valid_token
        
        # Create session and call method
        session = Session()
        result = session.get_attestation_token(self.test_url)
        
        # Verify result and attestor was called correctly
        self.assertEqual(result, self.valid_token)
        mock_attestor_instance.get_attestation_token.assert_called_once_with(
            self.test_url)

    @patch('lorica.session.Attestor')
    def test_get_attested_deployment_report(self, mock_attestor):
        """Test get_attested_deployment_report method"""
        # Setup mocks
        mock_attestor_instance = mock_attestor.return_value
        test_report = {"status": "verified"}
        mock_attestor_instance.get_attested_deployment_report.return_value = (
            test_report)
        
        # Create session and call method
        session = Session()
        result = session.get_attested_deployment_report(self.test_url)
        
        # Verify result and attestor was called correctly
        self.assertEqual(result, test_report)
        mock_attestor_instance.get_attested_deployment_report.assert_called_once_with(
            self.test_url)

if __name__ == '__main__':
    unittest.main() 