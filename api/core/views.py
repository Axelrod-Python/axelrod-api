from distutils.util import strtobool
from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
import axelrod as axl
from api.core.serializers import (
    strategy_id,
    MatchSerializer,
    StrategySerializer,
    TournamentSerializer,
)
from api.core.serializers import ResultsSerializer


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


class BaseGameView(viewsets.ViewSet):
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

    def create(self, request):
        """
        POST method

        Take in a game_definition which expects all of the
        required parameters of the type of game, a list of
        player strings, and starts the game.
        """
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            game_definition = serializer.data

            try:
                players = self._parse_players(request.data['player_list'])
                game_definition.pop('player_list')
            except KeyError as e:
                return Response({
                    'player_list': [self._not_found_error.format(e.args[0])]
                }, 400)

            results = self.run(players, game_definition)
            return Response(ResultsSerializer(results).data, 201)
        return Response(serializer.errors, 400)


class TournamentViewSet(BaseGameView):
    """
    View that handles the creation and retrieval of tournaments. A
    tournament consists of two or more players facing each other
    in a round robin bout.
    """

    serializer = TournamentSerializer

    @staticmethod
    def run(players, definition):
        tournament = axl.Tournament(players=players, **definition)
        return tournament.play()


class MatchViewSet(BaseGameView):
    """
    View that handles creation and retrieval of matches. A match
    is a 1v1 game between two players.
    """

    serializer = MatchSerializer

    @staticmethod
    def run(players, definition):
        match = axl.Match(players=players, **definition)
        return match.play()


