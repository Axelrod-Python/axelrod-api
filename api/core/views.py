from rest_framework import viewsets
from rest_framework.response import Response
import axelrod as axl
from api.core.serializers import StrategySerializer, strategy_id


class StrategyViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = StrategySerializer(
            axl.strategies, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        strategy_dict = {
            strategy_id(s): s for s in axl.strategies}
        strategy = strategy_dict[pk]
        serializer = StrategySerializer(strategy, context={'request': request})
        return Response(serializer.data)
