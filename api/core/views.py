from distutils.util import strtobool

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
import axelrod as axl
from api.core import models
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

from .utils import strategy_id


def filter_strategies(request):
    """
    Take the incoming request object, convert the strings in its
    query_params dictionary into the types required by the axelrod
    filtering function and pass the resulting dictionary into that
    filtering function.
    """

    params = request.query_params

    filter_types = {
        strtobool: [
            'stochastic',
            'long_run_time',
            'manipulates_state',
            'manipulates_source',
            'inpsects_source'
        ],
        int: [
            'memory_depth',
            'min_memory_depth',
            'max_memory_depth'
        ],
    }

    filterset = {
        _filter: convert_type(params[_filter])
        for convert_type, filters in filter_types.items()
        for _filter in filters if _filter in params
    }

    if 'makes_use_of' in params:
        filterset['makes_use_of'] = params.getlist('makes_use_of')
    return axl.filtered_strategies(filterset)


class StrategyViewSet(viewsets.ViewSet):

    strategies_index = {strategy_id(s): s for s in axl.strategies}

    def list(self, request):
        serializer = StrategySerializer(
            filter_strategies(request), many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            strategy = self.strategies_index[pk]
        except KeyError:
            raise Http404
        serializer = StrategySerializer(strategy, context={'request': request})
        return Response(serializer.data)


class GameViewSet(viewsets.ViewSet):
    """
    Base game object for ViewSets to inherit. Creates, retrieves and
    cancels games.
    """

    strategies_index = {strategy_id(s): s for s in axl.strategies}
    _not_found_error = 'Strategy not found: {}'

    def _parse_players(self, player_list):
        """
        convert list of player strings into list of Strategies

        Parameters
        ----------
            player_list: list of strings
                a list of player ids
        """
        players = []
        for player in player_list:
            strategy = self.strategies_index[player]
            players.append(strategy())
        return players

    def validate_and_create_strategies(self, player_list):
        """
        generate the axelrod Strategy from each player
        in the player list.

        Parameters
        ----------
            player_list: list of strings
                a list of player ids
        """
        # note that we must instantiate the strategy
        return [self.strategies_index[s]() for s in player_list]

    @staticmethod
    def create_players(strategy):
        """
        check to see if the internal strategy exists in
        the database and create it if not.

        Parameters
        ----------
            strategy: string
                strategy id
        """
        try:
            return InternalStrategy.objects.get(id=strategy)
        except ObjectDoesNotExist:
            return InternalStrategy.objects.create(id=strategy)

    def start(self, definition, strategies):
        """start a game based on definition and list of strategies"""
        game = self.model.objects.create(definition=definition, status=0)
        result = game.run(strategies)
        game.results = self.results_serializer(result).data
        game.save()
        return game

    def create(self, request):
        """
        Take in a game_definition which expects all of the
        required parameters of the type of game, a list of
        player strings, and starts the game.
        """
        try:
            strategies = self.validate_and_create_strategies(request.data['player_list'])
        except KeyError as e:
            return Response({
                'player_list': [self._not_found_error.format(e.args[0])]
            }, 400)

        # update Internal Strategy store
        [self.create_players(s) for s in request.data['player_list']]

        definition_serializer = self.definition_serializer(data=request.data)
        if definition_serializer.is_valid():
            definition = definition_serializer.save()
            game = self.start(definition, strategies)
            game_serializer = self.response_serializer(game)
            return Response(game_serializer.data, 201)
        return Response(definition_serializer.errors, 400)

    def list(self):
        """retrieve a list of all games of this type"""
        games = self.model.objects.all()
        serializer = self.response_serializer(games, many=True)
        return Response(serializer.data, 200)

    def retrieve(self, request, pk=None):
        """retrieve a specific game"""
        try:
            game = self.model.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise Http404
        serializer = self.response_serializer(game)
        return Response(serializer.data, 200)

    def destroy(self, request, pk=None):
        try:
            self.model.objects.get(id=pk).delete()
        except ObjectDoesNotExist:
            raise Http404
        return Response('Deleted')


class TournamentViewSet(GameViewSet):
    """
    View that handles the creation and retrieval of tournaments. A
    tournament consists of two or more players facing each other
    in a round robin bout.
    """

    definition_serializer = TournamentDefinitionSerializer
    definition_model = models.TournamentDefinition
    results_serializer = TournamentResultsSerializer
    response_serializer = TournamentSerializer
    model = models.Tournament


class MatchViewSet(GameViewSet):
    """
    View that handles creation and retrieval of matches. A match
    is a 1v1 game between two players.
    """

    definition_serializer = MatchDefinitionSerializer
    definition_model = models.MatchDefinition
    results_serializer = MatchResultsSerializer
    response_serializer = MatchSerializer
    model = models.Match


class MoranViewSet(GameViewSet):
    """
    View that handles the creation and retrieval of Moran
    Processes. This is a
    """

    definition_serializer = MoranDefinitionSerializer
    definition_model = models.MoranDefinition
    results_serializer = MoranResultsSerializer
    response_serializer = MoranSerializer
    model = models.MoranProcess


