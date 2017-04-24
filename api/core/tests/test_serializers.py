from unittest import TestCase
import axelrod as axl
from rest_framework.test import APIRequestFactory

from api.core.models import InternalStrategy
from api.core.serializers import (
    MatchSerializer,
    MatchDefinitionSerializer,
    MatchResultsSerializer,
    MoranSerializer,
    MoranDefinitionSerializer,
    MoranResultsSerializer,
    StrategySerializer,
    TournamentSerializer,
    TournamentDefinitionSerializer,
    TournamentResultsSerializer,
)


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
    params = {'rate': 0.5}

    def __init__(self):
        pass

    def init_params(self):
        return self.params


class TestStrategySerializer(TestCase):

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

    def test_handles_infinite_memory_depth_in_params(self):
        self.strategy.params = {'memory_depth': float('inf')}
        serializer = StrategySerializer(self.strategy, context={'request': self.request})
        self.assertEqual({'memory_depth': -1}, serializer.data['params'])


class TestTournamentDefinitionSerializer(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_post_data = {
            'name': 'test_tournament',
            'turns': 5,
            'repetitions': 2,
            'noise': 0.1,
            'with_morality': False,
            'player_list': ['test1', 'test2']
        }
        cls.missing_name = {
            'turns': 5,
            'repetitions': 2,
            'noise': 0.1,
            'with_morality': False,
            'player_list': ['test1', 'test2']
        }
        cls.invalid_field_values = {
            'name': 'test_tournament',
            'turns': 5,
            'repetitions': 2,
            'noise': 0.1,
            'with_morality': False,
            'player_list': ['test', 'test2']
        }
        InternalStrategy.objects.create(id='test1')
        InternalStrategy.objects.create(id='test2')

    @classmethod
    def tearDownClass(cls):
        InternalStrategy.objects.all().delete()

    def test_is_valid_with_all_fields(self):
        serializer = TournamentDefinitionSerializer(data=self.valid_post_data)
        self.assertTrue(serializer.is_valid())

    def test_is_invalid_with_missing_fields(self):
        serializer = TournamentDefinitionSerializer(data=self.missing_name)
        self.assertFalse(serializer.is_valid())
        self.assertEqual({'name': ['This field is required.']}, serializer.errors)

    def test_is_invalid_with_incorrect_value(self):
        serializer = TournamentDefinitionSerializer(data=self.invalid_field_values)
        self.assertFalse(serializer.is_valid())
        self.assertEqual({
            'player_list': ['Invalid pk "test" - object does not exist.']
        }, serializer.errors)


class TestMatchDefinitionSerializer(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_post_data = {
            'turns': 5,
            'noise': 0.1,
            'player_list': ['test1', 'test2']
        }
        cls.missing_turns = {
            'noise': 0.1,
            'player_list': ['test1', 'test2']
        }
        cls.invalid_field_values = {
            'turns': 5,
            'noise': 0.1,
            'player_list': ['test1']
        }
        InternalStrategy.objects.create(id='test1')
        InternalStrategy.objects.create(id='test2')

    @classmethod
    def tearDownClass(cls):
        InternalStrategy.objects.all().delete()

    def test_is_valid_with_all_fields(self):
        serializer = MatchDefinitionSerializer(data=self.valid_post_data)
        self.assertTrue(serializer.is_valid())

    def test_is_invalid_with_missing_fields(self):
        serializer = MatchDefinitionSerializer(data=self.missing_turns)
        self.assertFalse(serializer.is_valid())
        self.assertEqual({'turns': ['This field is required.']}, serializer.errors)

    def test_is_invalid_with_incorrect_value(self):
        serializer = MatchDefinitionSerializer(data=self.invalid_field_values)
        self.assertFalse(serializer.is_valid())
        self.assertEqual({
            'player_list': ['Ensure this field has exactly 2 elements.']
        }, serializer.errors)


class TestTournamentResultSerializer(TestCase):

    @classmethod
    def setUpClass(cls):
        players = [axl.Alternator(), axl.TitForTat()]
        tournament = axl.Tournament(players)
        cls.results = tournament.play()
        cls.data = TournamentResultsSerializer(cls.results).data
        cls.expected_keys = [
            'filename', 'num_interactions', 'players', 'repetitions',
            'nplayers', 'match_lengths', 'wins', 'scores', 'normalised_scores',
            'payoffs', 'score_diffs', 'cooperation', 'normalised_cooperation',
            'initial_cooperation_count', 'good_partner_matrix', 'total_interactions',
            'good_partner_rating', 'ranking', 'ranked_names', 'payoff_matrix',
            'payoff_stddevs', 'payoff_diffs_means', 'vengeful_cooperation',
            'cooperating_rating', 'initial_cooperation_rate', 'eigenjesus_rating',
            'eigenmoses_rating', 'wins',
        ]

    def test_data_keys_in_expected(self):
        for data_key, value in self.data.items():
            self.assertIn(data_key, self.expected_keys)

    def test_only_expected_in_data(self):
        for expected_key in self.expected_keys:
            self.assertIn(expected_key, self.data)

