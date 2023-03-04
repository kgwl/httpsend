from unittest import TestCase
import httpsend


class TestHttpsend(TestCase):

    def setUp(self):
        self.url = 'https://example.com'

    def test_get_type(self):
        self.response = httpsend.get(url=self.url, http_choice='all')
        self.assertEqual(type(self.response), dict)

    def test_get_choice(self):
        self.response = httpsend.get(url=self.url, http_choice='text')
        self.assertEqual(list(self.response.keys())[0], 'text')