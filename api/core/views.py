from rest_framework import serializers, viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
import axelrod as axl


def strategy_id(strategy):
    return strategy.name.lower().replace(' ', '')


class StrategySerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=200)
    description = serializers.SerializerMethodField()
    classifier = serializers.DictField()

    def get_id(self, strategy):
        return strategy_id(strategy)

    def get_url(self, strategy):
        request = self.context['request']
        return reverse(
            viewname='strategies-detail',
            args=[strategy_id(strategy)],
            request=request)

    def get_description(self, strategy):
        return strategy.__doc__


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
