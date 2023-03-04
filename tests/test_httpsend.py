import base64
from unittest import TestCase
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
        directory = 'outputfiles/'
        filename = base64.b64encode(self.url.encode('utf-8')).decode()
        path = directory + filename
        content = ''.join([random.choice(string.ascii_lowercase) for _ in range(10)])

        httpsend.save(path, content)

        file = open(path, 'r')
        result = file.read()
        file.close()

        self.assertEqual(result, content)

    def test_read_urls(self):
        filename = 'inputfiles/test_read_urls.txt'
        urls = httpsend.read_urls(filename)
        self.assertEqual(type(urls), list)
        self.assertEqual(urls[0], 'https://example.com')
        self.assertEqual(urls[1], 'https://google.com')
