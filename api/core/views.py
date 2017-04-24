from distutils.util import strtobool

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import viewsets
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

    def get_strategy_from_id(self, player_list):
        """
        retrieve the axelrod Strategy or each player
        in the player list and instantiate them.

        Parameters
        ----------
            player_list: list of strings
                a list of strategy ids
        """
        # note that the strategy is being instantiated - bugs with
        # misleading error messages will be generated if they are not
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

    def start_game(self, definition, players):
        """
        start a game based on definition and list of strategies

        Parameters
        ----------
            definition: GameDefinition
                definition class that contains all game parameters
            players: list of axelrod.Strategy
                **instantiated** axelrod Strategy classes that are
                playing the game
        """
        game = self.model.objects.create(definition=definition, status=0)
        result = game.run(players)
        game.results = self.results_serializer(result).data
        game.save()
        return game

    def create(self, request):
        """
        Take in a game definition from JSON post data which
        expects all of the required parameters of the game,
        a list of and a list of player strings. Once all of
        these are validated, start the game.
        """
        try:
            players = self.get_strategy_from_id(request.data['player_list'])
        except KeyError as e:
            # handle case where strategy id is not found in list of strategies
            return Response({
                'player_list': [self._not_found_error.format(e.args[0])]
            }, 400)

        # update Internal Strategy store
        [self.create_players(s) for s in request.data['player_list']]

        definition_serializer = self.definition_serializer(data=request.data)
        if definition_serializer.is_valid():
            definition = definition_serializer.save()
            game = self.start_game(definition, players)
            return Response(self.game_serializer(game).data, 201)
        return Response(definition_serializer.errors, 400)

    def list(self, request):
        """retrieve a list of all games of this type"""
        games = self.model.objects.all()
        serializer = self.game_serializer(games, many=True)
        return Response(serializer.data, 200)

    def retrieve(self, request, pk=None):
        """retrieve a specific game"""
        try:
            game = self.model.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise Http404
        serializer = self.game_serializer(game)
        return Response(serializer.data, 200)

    def destroy(self, request, pk=None):
        """delete a specific game"""
        try:
            self.model.objects.get(id=pk).delete()
        except ObjectDoesNotExist:
            raise Http404
        return Response(status=204)


class TournamentViewSet(GameViewSet):
    """
    View that handles the creation and retrieval of tournaments. A
    tournament consists of two or more players facing each other
    in a round robin bout.
    """

    definition_serializer = TournamentDefinitionSerializer
    definition_model = models.TournamentDefinition
    results_serializer = TournamentResultsSerializer
    game_serializer = TournamentSerializer
    model = models.Tournament


class MatchViewSet(GameViewSet):
    """
    View that handles creation and retrieval of matches. A match
    is a 1v1 game between two players.
    """

    definition_serializer = MatchDefinitionSerializer
    definition_model = models.MatchDefinition
    results_serializer = MatchResultsSerializer
    game_serializer = MatchSerializer
    model = models.Match


class MoranViewSet(GameViewSet):
    """
    View that handles the creation and retrieval of Moran
    Processes.
    """

    definition_serializer = MoranDefinitionSerializer
    definition_model = models.MoranDefinition
    results_serializer = MoranResultsSerializer
    game_serializer = MoranSerializer
    model = models.MoranProcess


