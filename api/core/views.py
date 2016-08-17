from rest_framework import viewsets
from rest_framework.response import Response
import axelrod as axl
from api.core.serializers import StrategySerializer, strategy_id
from api.core.filters import passes_filterset


def strategies(request):
    return [
        s for s in axl.all_strategies
        if passes_filterset(s, request.query_params)]


class StrategyViewSet(viewsets.ViewSet):

    strategies_index = {strategy_id(s): s for s in axl.strategies}

    def list(self, request):
        serializer = StrategySerializer(
            strategies(request), many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        strategy = self.strategies_index[pk]
        serializer = StrategySerializer(strategy, context={'request': request})
        return Response(serializer.data)
