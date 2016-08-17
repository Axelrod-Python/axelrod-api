import unittest
from api.core.filters import passes_filterset, passes_boolean_filter


class TestStrategy(object):

    classifier = {
        'stochastic': True
    }


class TestFilters(unittest.TestCase):

    def test_match_stochastic(self):
        test_strategy = TestStrategy()
        test_filterset = {'stochastic': 'True'}
        self.assertTrue(passes_boolean_filter(
            test_strategy, test_filterset, 'stochastic'))

    def test_match_params(self):
        test_strategy = TestStrategy()
        test_filterset = {'stochastic': 'True'}
        self.assertTrue(passes_filterset(test_strategy, test_filterset))
        self.assertTrue(passes_filterset(test_strategy, {}))
