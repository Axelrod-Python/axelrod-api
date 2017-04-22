import json
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


class TestTournamentView(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_post_data = {
            'name': 'tournament',
            'turns': 5,
            'repetitions': 2,
            'noise': 0.1,
            'with_morality': False,
            'player_list': ["adaptive", "allcoralld", "adaptive", "anticycler"],
        }
        cls.no_strategy_found = {
            'name': 'tournament',
            'turns': 5,
            'repetitions': 2,
            'noise': 0.1,
            'with_morality': False,
            'player_list': ["adapt", "allcoralld"],
        }
        cls.missing_name = {
            'turns': 5,
            'repetitions': 2,
            'noise': 0.1,
            'with_morality': False,
            'player_list': ["adaptive", "allcoralld", "adaptive", "anticycler"],
        }

    def setUp(self):
        self.client = APIClient()

    @mock.patch('api.core.views.ResultsSerializer')
    def test_tournament_played(self, serializer):
        mock_object = mock.MagicMock
        mock_object.data = 'test'

        serializer.return_value = mock_object()
        response = self.client.post('/tournaments/',
                                    json.dumps(self.valid_post_data),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, serializer.call_count)

    @mock.patch('api.core.views.ResultsSerializer')
    @mock.patch('api.core.views.axl.Tournament.play')
    def test_strategy_not_found(self, play, serializer):
        mock_object = mock.MagicMock
        mock_object.data = 'test'

        serializer.return_value = mock_object()
        response = self.client.post('/tournaments/',
                                    json.dumps(self.no_strategy_found),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)
        self.assertEqual({
            'player_list': ['Strategy not found: adapt']},
            response.data)

    @mock.patch('api.core.views.ResultsSerializer')
    @mock.patch('api.core.views.axl.Tournament.play')
    def test_invalid_field(self, play, serializer):
        mock_object = mock.MagicMock
        mock_object.data = 'test'

        serializer.return_value = mock_object()
        response = self.client.post('/tournaments/',
                                    json.dumps(self.missing_name),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)
        self.assertEqual({'name': ['This field is required.']}, response.data)


class TestMatchView(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_post_data = {
            'turns': 5,
            'noise': 0.1,
            'player_list': ["adaptive", "allcoralld"],
        }
        cls.no_strategy_found = {
            'turns': 5,
            'noise': 0.1,
            'player_list': ["adapt"],
        }
        cls.missing_noise = {
            'turns': 5,
            'player_list': ["adaptive", "allcoralld"],
        }

    def setUp(self):
        self.client = APIClient()

    @mock.patch('api.core.views.ResultsSerializer')
    def test_match_played(self, serializer):
        """run this without mocking run"""
        mock_object = mock.MagicMock
        mock_object.data = 'test'

        serializer.return_value = mock_object()
        response = self.client.post('/matches/',
                                    json.dumps(self.valid_post_data),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)

    @mock.patch('api.core.views.ResultsSerializer')
    @mock.patch('api.core.views.axl.Match.play')
    def test_strategy_not_found(self, play, serializer):
        mock_object = mock.MagicMock
        mock_object.data = 'test'

        serializer.return_value = mock_object()
        response = self.client.post('/matches/',
                                    json.dumps(self.no_strategy_found),
                                    content_type='application/json')
        self.assertEqual({
            'player_list': ['Ensure this field has at least 2 elements.']},
            response.data)
        self.assertEqual(400, response.status_code)

    @mock.patch('api.core.views.ResultsSerializer')
    @mock.patch('api.core.views.axl.Match.play')
    def test_invalid_field(self, play, serializer):
        mock_object = mock.MagicMock
        mock_object.data = 'test'

        serializer.return_value = mock_object()
        response = self.client.post('/matches/',
                                    json.dumps(self.missing_noise),
                                    content_type='application/json')
        self.assertEqual({'noise': ['This field is required.']}, response.data)
        self.assertEqual(400, response.status_code)




