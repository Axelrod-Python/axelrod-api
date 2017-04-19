from unittest import TestCase, mock
from rest_framework.test import APIRequestFactory


from api.core.views import filter_strategies


class TestStrategy(object):

    classifier = {
        'stochastic': True
    }

    def __init__(self, classifier):
        self.classifier = classifier


class TestFilterStrategies(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = APIRequestFactory()

    @mock.patch('api.core.views.axl.filtered_strategies')
    def test_string_word_to_boolean(self, filtered_strategies_mock):
        filtered_strategies_mock.return_value = mock.MagicMock()

        request = self.factory.get('/articles/?stochastic=true')
        request.query_params = request.GET  # factory doesn't support query_params
        filter_strategies(request)
        filtered_strategies_mock.assert_called_with({'stochastic': 1})

    @mock.patch('api.core.views.axl.filtered_strategies')
    def test_string_number_to_boolean(self, filtered_strategies_mock):
        mock.return_value = mock.MagicMock()

        request = self.factory.get('/articles/?stochastic=1')
        request.query_params = request.GET  # factory doesn't support query_params
        filter_strategies(request)
        filtered_strategies_mock.assert_called_with({'stochastic': 1})

    @mock.patch('api.core.views.axl.filtered_strategies')
    def test_string_to_int(self, filtered_strategies_mock):
        filtered_strategies_mock.return_value = mock.MagicMock()

        request = self.factory.get('/articles/?memory_depth=3')
        request.query_params = request.GET  # factory doesn't support query_params
        filter_strategies(request)
        filtered_strategies_mock.assert_called_with({'memory_depth': 3})

    @mock.patch('api.core.views.axl.filtered_strategies')
    def test_makes_use_of(self, filtered_strategies_mock):
        filtered_strategies_mock.return_value = mock.MagicMock()

        request = self.factory.get('/articles/?makes_use_of=game')
        request.query_params = request.GET  # factory doesn't support query_params
        filter_strategies(request)
        filtered_strategies_mock.assert_called_with({'makes_use_of': ['game']})

