import unittest
from api.core.filters import passes_filterset, passes_boolean_filter


class TestStrategy(object):

    classifier = {
        'stochastic': True
    }


class TestFilters(unittest.TestCase):

    def test_passes_boolean_filter(self):
        test_strategy = TestStrategy()

        # test that filter works with a string value
        test_filterset = {'stochastic': 'True'}
        self.assertTrue(passes_boolean_filter(
            test_strategy, test_filterset, 'stochastic'))

        # test that filter works with a boolean value
        test_filterset = {'stochastic': True}
        self.assertTrue(passes_boolean_filter(
            test_strategy, test_filterset, 'stochastic'))

    def test_passes_filterset(self):
        test_strategy = TestStrategy()
        test_filterset = {'stochastic': 'True'}
        self.assertTrue(passes_filterset(test_strategy, test_filterset))
        self.assertTrue(passes_filterset(test_strategy, {}))
