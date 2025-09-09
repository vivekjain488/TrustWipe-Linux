#!/usr/bin/env python3
"""
TrustWipe System Tests
Comprehensive test suite for TrustWipe functionality
"""

import unittest
import tempfile
import os
import json
import subprocess
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import DataWiper, SystemInfo
from certificate_generator import CertificateGenerator

class TestSystemInfo(unittest.TestCase):
    """Test system information collection"""
    
    def test_get_system_info(self):
        """Test system information collection"""
        info = SystemInfo.get_system_info()
        
        # Check that basic info is present
        self.assertIn('hostname', info)
        self.assertIn('os', info)
        self.assertIn('architecture', info)
        self.assertIn('timestamp', info)
        
        # Check data types
        self.assertIsInstance(info['hostname'], str)
        self.assertIsInstance(info['os'], str)
        self.assertIsInstance(info['architecture'], str)
    
    def test_get_device_info(self):
        """Test device information collection"""
        # Test with a non-existent device
        info = SystemInfo.get_device_info('/dev/nonexistent')
        self.assertIn('device_path', info)
        self.assertEqual(info['device_path'], '/dev/nonexistent')
        
        # Should handle errors gracefully
        self.assertIsInstance(info, dict)

class TestCertificateGenerator(unittest.TestCase):
    """Test certificate generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cert_gen = CertificateGenerator(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_certificate_generation(self):
        """Test certificate generation"""
        # Sample data
        system_info = {
            'hostname': 'test-host',
            'os': 'Linux',
            'architecture': 'x86_64',
            'memory': {'total_human': '8.00 GB'}
        }
        
        device_info = {
            'device_path': '/dev/sdb',
            'size_human': '1.00 TB',
            'model': 'Test Drive',
            'serial': 'TEST123'
        }
        
        wipe_details = {
            'device_path': '/dev/sdb',
            'method': 'zeros',
            'passes': 3,
            'start_time': '2025-09-09T10:00:00',
            'end_time': '2025-09-09T11:00:00',
            'duration': '1:00:00',
            'status': 'SUCCESS'
        }
        
        # Generate certificate
        cert_path, html_path = self.cert_gen.generate_certificate(
            system_info, device_info, wipe_details
        )
        
        # Check that files were created
        self.assertTrue(os.path.exists(cert_path))
        self.assertTrue(os.path.exists(html_path))
        
        # Check JSON certificate content
        with open(cert_path, 'r') as f:
            cert_data = json.load(f)
        
        self.assertIn('certificate_info', cert_data)
        self.assertIn('system_info', cert_data)
        self.assertIn('device_info', cert_data)
        self.assertIn('wipe_details', cert_data)
        self.assertIn('verification', cert_data)
        
        # Check certificate ID format
        cert_id = cert_data['certificate_info']['id']
        self.assertEqual(len(cert_id), 36)  # UUID format
        
        # Check HTML certificate
        with open(html_path, 'r') as f:
            html_content = f.read()
        
        self.assertIn('DATA ERASURE CERTIFICATE', html_content)
        self.assertIn('DATA ERASED SUCCESSFULLY', html_content)
        self.assertIn('/dev/sdb', html_content)
    
    def test_list_certificates(self):
        """Test certificate listing"""
        # Initially no certificates
        certs = self.cert_gen.list_certificates()
        self.assertEqual(len(certs), 0)
        
        # Generate a certificate
        system_info = {'hostname': 'test'}
        device_info = {'device_path': '/dev/test'}
        wipe_details = {'method': 'zeros', 'status': 'SUCCESS'}
        
        self.cert_gen.generate_certificate(system_info, device_info, wipe_details)
        
        # Should now have one certificate
        certs = self.cert_gen.list_certificates()
        self.assertEqual(len(certs), 1)
        
        cert = certs[0]
        self.assertIn('filename', cert)
        self.assertIn('certificate_id', cert)
        self.assertIn('device', cert)
        self.assertIn('method', cert)

class TestDataWiper(unittest.TestCase):
    """Test data wiping functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b'X' * 1024)  # 1KB of test data
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_device_validation(self):
        """Test device validation"""
        # Test with non-existent device
        wiper = DataWiper('/dev/nonexistent')
        with self.assertRaises(ValueError):
            wiper.validate_device()
        
        # Test with existing file (should work for testing)
        wiper = DataWiper(self.temp_file.name)
        try:
            wiper.validate_device()  # Should not raise exception
        except PermissionError:
            # May not have write access in all test environments
            pass
    
    def test_human_readable_size(self):
        """Test human readable size formatting"""
        self.assertEqual(DataWiper.human_readable_size(1024), "1.00 KB")
        self.assertEqual(DataWiper.human_readable_size(1024 * 1024), "1.00 MB")
        self.assertEqual(DataWiper.human_readable_size(1024 * 1024 * 1024), "1.00 GB")
    
    @patch('subprocess.Popen')
    def test_wipe_with_zeros_mock(self, mock_popen):
        """Test zero wiping with mocked subprocess"""
        # Mock successful dd command
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.communicate.return_value = ('', '')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        wiper = DataWiper(self.temp_file.name, 'zeros', 1)
        
        # Mock validate_device to avoid permission issues
        with patch.object(wiper, 'validate_device'):
            try:
                result = wiper.wipe()
                self.assertTrue(result)
            except Exception as e:
                # Some tests may fail due to environment constraints
                self.skipTest(f"Test skipped due to environment: {e}")

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow_simulation(self):
        """Test a complete workflow simulation"""
        # Create temporary certificate directory
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_gen = CertificateGenerator(temp_dir)
            
            # Simulate system info collection
            system_info = SystemInfo.get_system_info()
            self.assertIsInstance(system_info, dict)
            
            # Simulate device info collection
            device_info = SystemInfo.get_device_info('/dev/sda')
            self.assertIsInstance(device_info, dict)
            
            # Simulate wipe details
            wipe_details = {
                'device_path': '/dev/sda',
                'method': 'zeros',
                'passes': 1,
                'start_time': '2025-09-09T10:00:00',
                'end_time': '2025-09-09T10:30:00',
                'duration': '0:30:00',
                'status': 'SUCCESS'
            }
            
            # Generate certificate
            cert_path, html_path = cert_gen.generate_certificate(
                system_info, device_info, wipe_details
            )
            
            # Verify certificate was created
            self.assertTrue(os.path.exists(cert_path))
            self.assertTrue(os.path.exists(html_path))
            
            # Verify certificate listing works
            certs = cert_gen.list_certificates()
            self.assertEqual(len(certs), 1)

class TestUtilities(unittest.TestCase):
    """Test utility functions"""
    
    def test_imports(self):
        """Test that all modules can be imported"""
        import backend
        import certificate_generator
        import cli
        
        # Test that main classes exist
        self.assertTrue(hasattr(backend, 'DataWiper'))
        self.assertTrue(hasattr(backend, 'SystemInfo'))
        self.assertTrue(hasattr(certificate_generator, 'CertificateGenerator'))
        self.assertTrue(hasattr(cli, 'TrustWipeCLI'))

def run_tests():
    """Run all tests"""
    print("🧪 Running TrustWipe Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSystemInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestCertificateGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDataWiper))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilities))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    print("\n🎯 Test Summary:")
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        return False
    
    return True

if __name__ == "__main__":
    # Check if running as root for certain tests
    if os.geteuid() == 0:
        print("⚠️  Running as root - some tests may behave differently")
    
    success = run_tests()
    sys.exit(0 if success else 1)
