import json
from unittest import TestCase, mock
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from api.core.serializers import strategy_id
from api.core.models import (
    InternalStrategy, MoranProcess, MoranDefinition, Tournament,
    TournamentDefinition,
    Match, MatchDefinition)


class TestStrategy(object):

    def __init__(self, name, classifier):
        self.name = name
        self.classifier = classifier

    def init_params(self):
        return {}


class TestGame(object):

    def __init__(self):
        pass


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


class TestTournamentPostView(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tournament1 = Tournament(id=3)
        cls.valid_post_data = {
            'id': 10,
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
        cls.one_strategy = {
            'name': 'tournament',
            'turns': 5,
            'repetitions': 2,
            'noise': 0.1,
            'with_morality': False,
            'player_list': ["adaptive"],
        }
        InternalStrategy.objects.create(id='adaptive')
        InternalStrategy.objects.create(id='allcoralld')

    @classmethod
    def tearDownClass(cls):
        InternalStrategy.objects.all().delete()

    def setUp(self):
        self.client = APIClient()

    @mock.patch('api.core.models.Tournament.save', mock.MagicMock)
    def test_tournament_played(self):
        response = self.client.post('/tournaments/',
                                    json.dumps(self.valid_post_data),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)

    def test_strategy_not_found(self):
        response = self.client.post('/tournaments/',
                                    json.dumps(self.no_strategy_found),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)
        self.assertEqual({
            'player_list': ['Strategy not found: adapt']},
            response.data)

    def test_invalid_field(self):
        response = self.client.post('/tournaments/',
                                    json.dumps(self.missing_name),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)
        self.assertEqual({'name': ['This field is required.']}, response.data)

    def test_invalid_strategy_count(self):
        response = self.client.post('/tournaments/',
                                    json.dumps(self.one_strategy),
                                    content_type='application/json')
        self.assertEqual({'player_list': ['Ensure this field has at least 2 elements.']}, response.data)
        self.assertEqual(400, response.status_code)


class TestTournamentGetView(TestCase):

    @classmethod
    def setUpClass(cls):
        definition = TournamentDefinition.objects.create(
            id=1, turns=5, repetitions=5, noise=0.1, with_morality=True)
        Tournament.objects.create(id=1, status=2, definition=definition)
        Tournament.objects.create(id=2, status=2, definition=definition)
        Tournament.objects.create(id=3, status=0, definition=definition)
        Tournament.objects.create(id=4, status=3, definition=definition)

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        Tournament.objects.all().delete()
        TournamentDefinition.objects.all().delete()

    def test_retrieves_all(self):
        response = self.client.get('/tournaments/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(4, len(response.data))

    def test_retrieves_one(self):
        response = self.client.get('/tournaments/2/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.data['id'])
        self.assertEqual(2, response.data['status'])

    def test_id_does_not_exist(self):
        response = self.client.get('/tournaments/10/')
        self.assertEqual(404, response.status_code)


class TestTournamentDeleteView(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User(username='test')
        cls.admin = User(username='admin', is_staff=True)
        definition = TournamentDefinition.objects.create(
            id=1, turns=5, repetitions=5, noise=0.1, with_morality=True)
        Tournament.objects.create(id=5, status=2, definition=definition)
        Tournament.objects.create(id=6, status=2, definition=definition)

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        Tournament.objects.all().delete()
        TournamentDefinition.objects.all().delete()

    def test_rejects_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete('/tournaments/5/')
        self.assertEqual(403, response.status_code)

    def test_rejects_no_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/tournaments/5/')
        self.assertEqual(403, response.status_code)

    def test_deletes_correct_id(self):
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(2, len(Tournament.objects.all()))
        response = self.client.delete('/tournaments/5/')
        self.assertEqual(1, len(Tournament.objects.all()))
        self.assertEqual(204, response.status_code)

    def test_id_does_not_exist(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/tournaments/10/')
        self.assertEqual(404, response.status_code)


class TestMatchPostView(TestCase):

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
            'player_list': ["adapt", 'allcoralld'],
        }
        cls.missing_noise = {
            'turns': 5,
            'player_list': ["adaptive", "allcoralld"],
        }
        cls.one_strategy = {
            'turns': 5,
            'noise': 0.1,
            'player_list': ["adaptive"],
        }
        InternalStrategy.objects.create(id='adaptive')
        InternalStrategy.objects.create(id='allcoralld')

    @classmethod
    def tearDownClass(cls):
        InternalStrategy.objects.all().delete()
        MatchDefinition.objects.all().delete()

    def setUp(self):
        self.client = APIClient()

    @mock.patch('api.core.models.Match.save', mock.MagicMock)
    def test_match_played(self):
        response = self.client.post('/matches/',
                                    json.dumps(self.valid_post_data),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)

    def test_strategy_not_found(self):
        response = self.client.post('/matches/',
                                    json.dumps(self.no_strategy_found),
                                    content_type='application/json')
        self.assertEqual({
            'player_list': ['Strategy not found: adapt']},
            response.data)
        self.assertEqual(400, response.status_code)

    def test_invalid_field(self):
        response = self.client.post('/matches/',
                                    json.dumps(self.missing_noise),
                                    content_type='application/json')
        self.assertEqual({'noise': ['This field is required.']}, response.data)
        self.assertEqual(400, response.status_code)

    def test_invalid_strategy_count(self):
        mock_object = mock.MagicMock
        mock_object.data = 'test'

        response = self.client.post('/matches/',
                                    json.dumps(self.one_strategy),
                                    content_type='application/json')
        self.assertEqual({'player_list': ['Ensure this field has exactly 2 elements.']}, response.data)
        self.assertEqual(400, response.status_code)


class TestMatchGetView(TestCase):

    @classmethod
    def setUpClass(cls):
        definition = MatchDefinition.objects.create(
            id=1, turns=5, noise=0.1)
        Match.objects.create(id=1, status=2, definition=definition)
        Match.objects.create(id=2, status=2, definition=definition)
        Match.objects.create(id=3, status=0, definition=definition)
        Match.objects.create(id=4, status=3, definition=definition)

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        Match.objects.all().delete()
        MatchDefinition.objects.all().delete()

    def test_retrieves_all(self):
        response = self.client.get('/matches/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(4, len(response.data))

    def test_retrieves_one(self):
        response = self.client.get('/matches/2/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.data['id'])
        self.assertEqual(2, response.data['status'])

    def test_id_does_not_exist(self):
        response = self.client.get('/matches/10/')
        self.assertEqual(404, response.status_code)


class TestMatchDeleteView(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User(username='test')
        cls.admin = User(username='admin', is_staff=True)
        definition = MatchDefinition.objects.create(
            id=1, turns=5, noise=0.1)
        Match.objects.create(id=5, status=2, definition=definition)
        Match.objects.create(id=6, status=0, definition=definition)

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        Match.objects.all().delete()
        MatchDefinition.objects.all().delete()

    def test_rejects_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete('/matches/5/')
        self.assertEqual(403, response.status_code)

    def test_rejects_no_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/matches/5/')
        self.assertEqual(403, response.status_code)

    def test_deletes_correct_id(self):
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(2, len(Match.objects.all()))
        response = self.client.delete('/matches/5/')
        self.assertEqual(1, len(Match.objects.all()))
        self.assertEqual(204, response.status_code)

    def test_id_does_not_exist(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/matches/10/')
        self.assertEqual(404, response.status_code)


class TestMoranProcessPostView(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.moran = MoranProcess(id=3)
        cls.valid_post_data = {
            'id': 10,
            'name': 'tournament',
            'turns': 5,
            'noise': 0.1,
            'mode': 'bd',
            'player_list': ["adaptive", "allcoralld", "adaptive", "anticycler"],
        }
        cls.no_strategy_found = {
            'name': 'tournament',
            'turns': 5,
            'noise': 0.1,
            'mode': 'bd',
            'player_list': ["adapt", "allcoralld"],
        }
        cls.missing_mode = {
            'turns': 5,
            'noise': 0.1,
            'player_list': ["adaptive", "allcoralld", "adaptive", "anticycler"],
        }
        cls.one_strategy = {
            'id': 10,
            'name': 'tournament',
            'turns': 5,
            'noise': 0.1,
            'mode': 'bd',
            'player_list': ["adaptive"],
        }
        InternalStrategy.objects.create(id='adaptive')
        InternalStrategy.objects.create(id='allcoralld')

    @classmethod
    def tearDownClass(cls):
        InternalStrategy.objects.all().delete()

    def setUp(self):
        self.client = APIClient()

    @mock.patch('api.core.models.MoranProcess.save', mock.MagicMock)
    def test_moran_played(self):
        response = self.client.post('/moran/',
                                    json.dumps(self.valid_post_data),
                                    content_type='application/json')
        self.assertEqual(201, response.status_code)

    def test_strategy_not_found(self):
        response = self.client.post('/moran/',
                                    json.dumps(self.no_strategy_found),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)
        self.assertEqual({
            'player_list': ['Strategy not found: adapt']},
            response.data)

    def test_invalid_field(self):
        response = self.client.post('/moran/',
                                    json.dumps(self.missing_mode),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)
        self.assertEqual({'mode': ['This field is required.']}, response.data)

    def test_invalid_strategy_count(self):
        response = self.client.post('/moran/',
                                    json.dumps(self.one_strategy),
                                    content_type='application/json')
        self.assertEqual({'player_list': ['Ensure this field has at least 2 elements.']}, response.data)
        self.assertEqual(400, response.status_code)


class TestMoranProcessGetView(TestCase):

    @classmethod
    def setUpClass(cls):
        definition = MoranDefinition.objects.create(
            id=1, turns=5, noise=0.1, mode='bd')
        MoranProcess.objects.create(id=1, status=2, definition=definition)
        MoranProcess.objects.create(id=2, status=2, definition=definition)
        MoranProcess.objects.create(id=3, status=0, definition=definition)
        MoranProcess.objects.create(id=4, status=3, definition=definition)

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        MoranProcess.objects.all().delete()
        MoranDefinition.objects.all().delete()

    def test_retrieves_all(self):
        response = self.client.get('/moran/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(4, len(response.data))

    def test_retrieves_one(self):
        response = self.client.get('/moran/2/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.data['id'])
        self.assertEqual(2, response.data['status'])

    def test_id_does_not_exist(self):
        response = self.client.get('/moran/10/')
        self.assertEqual(404, response.status_code)


class TestMoranProcessDeleteView(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User(username='test')
        cls.admin = User(username='admin', is_staff=True)
        definition = MoranDefinition.objects.create(
            id=1, turns=5, mode='bd', noise=0.1)
        MoranProcess.objects.create(id=5, status=2, definition=definition)
        MoranProcess.objects.create(id=6, status=2, definition=definition)

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        MoranProcess.objects.all().delete()
        MoranDefinition.objects.all().delete()

    def test_rejects_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete('/moran/5/')
        self.assertEqual(403, response.status_code)

    def test_rejects_no_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/moran/5/')
        self.assertEqual(403, response.status_code)

    def test_deletes_correct_id(self):
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(2, len(MoranProcess.objects.all()))
        response = self.client.delete('/moran/5/')
        self.assertEqual(1, len(MoranProcess.objects.all()))
        self.assertEqual(204, response.status_code)

    def test_id_does_not_exist(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/moran/10/')
        self.assertEqual(404, response.status_code)


