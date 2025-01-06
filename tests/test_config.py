import unittest
from app import app

class TestConfig(unittest.TestCase):
    def test_app_exists(self):
        self.assertTrue(app is not None)
        
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'] is not None)

if __name__ == '__main__':
    unittest.main()
