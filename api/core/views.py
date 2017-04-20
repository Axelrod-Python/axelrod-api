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


class BaseTournamentView:
    """

    """

    strategies_index = {strategy_id(s): s for s in axl.strategies}
    _not_found_error = 'Strategy {} was not found'

    def parse_players(self, player_list):
        players = []
        for player in player_list:
            strategy = self.strategies_index[player]
            players.append(strategy())
        return players

    def create(self, request):
        data = request.data
        serializer = self.serializer(data=data)
        if serializer.is_valid():
            tournament_definition = serializer.data
            try:
                players = self.parse_players(data['player_list'])
            except KeyError as e:
                return Response({'player_list': self._not_found_error.format(e.args[0])})

            results = self.run(players, tournament_definition)
            return Response(ResultsSerializer(results).data, 200)
        return Response(serializer.errors, 400)


class TournamentViewSet(viewsets.ViewSet, BaseTournamentView):

    serializer = TournamentSerializer

    @staticmethod
    def run(players, definition):
        tournament = axl.Tournament(players=players, **definition)
        return tournament.play()


class MatchViewSet(viewsets.ViewSet, BaseTournamentView):

    serializer = MatchSerializer

    @staticmethod
    def run(players, definition):
        match = axl.Match(players=players, **definition)
        return match.play()
