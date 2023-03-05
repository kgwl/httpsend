import base64
from unittest import TestCase
from unittest.mock import patch
import httpsend
import random
import string


class TestHttpsend(TestCase):

    def setUp(self):
        self.url = 'https://example.com'

    def test_get_type(self):
        self.response = httpsend.get(url=self.url, http_choice='all')
        self.assertEqual(type(self.response), dict)

    def test_get_choice(self):
        self.response = httpsend.get(url=self.url, http_choice='text')
        self.assertEqual(list(self.response.keys())[0], 'text')

    def test_save(self):
        directory = 'output-files/'
        filename = base64.b64encode(self.url.encode('utf-8')).decode()
        path = directory + filename
        content = ''.join([random.choice(string.ascii_lowercase) for _ in range(10)])

        httpsend.save(path, content)

        file = open(path, 'r')
        result = file.read()
        file.close()

        self.assertEqual(result, content)

    def test_read_urls_file(self):
        filename = 'input-files/test_read_urls.txt'
        urls = httpsend.read_urls(filename)
        self.assertEqual(type(urls), list)
        self.assertEqual(urls[0], 'https://example.com')
        self.assertEqual(urls[1], 'https://google.com')

    @patch('builtins.open')
    def test_read_urls_open(self, mock_system):
        filename = 'input-files/test_read_urls.txt'
        httpsend.read_urls(filename)
        mock_system.assert_called()

    def test_read_urls_single_url(self):
        url = 'https://example.com'
        urls = httpsend.read_urls(url)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], url)

    def test_is_url_true(self):
        url = 'https://example.com'
        result = httpsend.is_url(url)
        self.assertTrue(result)

    def test_is_url_false(self):
        url = 'test'
        result = httpsend.is_url(url)
        self.assertFalse(result)
