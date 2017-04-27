from unittest import TestCase

from api.config import wsgi


class TestWsgi(TestCase):

    def test_wsgi_executes_successfully(self):
        application = wsgi.application
        self.assertIsNotNone(application)

