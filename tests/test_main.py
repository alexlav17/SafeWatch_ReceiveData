import unittest
from src.main import app

class MainAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_api_endpoint(self):
        response = self.app.get('/api/data')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()