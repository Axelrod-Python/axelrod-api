from distutils.util import strtobool
from rest_framework import viewsets
from rest_framework.response import Response
import axelrod as axl
from api.core.serializers import StrategySerializer, strategy_id


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
        strategy = self.strategies_index[pk]
        serializer = StrategySerializer(strategy, context={'request': request})
        return Response(serializer.data)
