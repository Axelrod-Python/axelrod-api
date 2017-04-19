from unittest import TestCase, mock
from rest_framework.test import APIClient

from api.core.serializers import strategy_id


class TestStrategy(object):

    def __init__(self, name, classifier):
        self.name = name
        self.classifier = classifier

    def init_params(self):
        return {}


class TestStrategyView(TestCase):
    strategies = [
        TestStrategy('Test One', {'stochastic': True, 'memory_depth': 1}),
        TestStrategy('Test Two', {'stochastic': True, 'memory_depth': 1}),
        TestStrategy('Test Three', {'stochastic': True, 'memory_depth': 2}),
        TestStrategy('Test Four', {'stochastic': False, 'memory_depth': 2}),
        TestStrategy('Test Five', {'stochastic': False, 'memory_depth': 1}),
    ]
    strategies_index = {strategy_id(s): s for s in strategies}

    def setUp(self):
        self.client = APIClient()

    @mock.patch('api.core.views.axl.filtered_strategies')
    def test_lists_all_strategies(self, filtered_strategies):
        filtered_strategies.return_value = self.strategies
        response = self.client.get('/strategies/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.data))

    @mock.patch('api.core.views.StrategyViewSet.strategies_index', strategies_index)
    def test_retrieves_one_strategy(self):
        response = self.client.get('/strategies/testone/')
        self.assertEqual(200, response.status_code)
        self.assertEqual('Test One', response.data['name'])

    @mock.patch('api.core.views.StrategyViewSet.strategies_index', strategies_index)
    def test_strategy_does_not_exist(self):
        response = self.client.get('/strategies/notfound/')
        self.assertEqual(404, response.status_code)



