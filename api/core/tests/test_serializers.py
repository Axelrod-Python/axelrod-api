from unittest import TestCase
from rest_framework.test import APIRequestFactory

from api.core.serializers import StrategySerializer


class TestStrategy(object):
    name = 'Test Strategy'
    description = 'test object for serializer testing'
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "makes_use_of": [],
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        pass

    def init_params(self):
        return {
            'rate': 0.5
        }


class TestSerializers(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = APIRequestFactory()
        cls.request = cls.factory.get('/articles/')

    def setUp(self):
        self.strategy = TestStrategy()

    def test_has_correct_fields(self):
        serializer = StrategySerializer(self.strategy, context={'request': self.request})
        for key in ['url', 'id', 'name', 'description', 'classifier', 'params']:
            self.assertIn(key, serializer.data)

    def test_generates_correct_url(self):
        serializer = StrategySerializer(self.strategy, context={'request': self.request})
        self.assertEqual('http://testserver/strategies/teststrategy/', serializer.data['url'])

    def test_generates_correct_params(self):
        serializer = StrategySerializer(self.strategy, context={'request': self.request})
        self.assertEqual({'rate': 0.5}, serializer.data['params'])

    def test_handles_infinite_memory_depth(self):
        self.strategy.classifier['memory_depth'] = float('inf')
        serializer = StrategySerializer(self.strategy, context={'request': self.request})
        self.assertEqual(-1, serializer.data['classifier']['memory_depth'])

