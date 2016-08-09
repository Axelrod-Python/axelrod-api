from rest_framework import serializers, viewsets
from rest_framework.response import Response
import axelrod as axl


def id_from_name(name):
    return name.lower().replace(' ', '')


class StrategySerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=200)
    description = serializers.SerializerMethodField()
    classifier = serializers.DictField()

    def get_id(self, strategy):
        return id_from_name(strategy.name)

    def get_description(self, strategy):
        return strategy.__doc__


class StrategyViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = StrategySerializer(axl.strategies, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        strategy_dict = {
            id_from_name(s.name): s for s in axl.strategies}
        strategy = strategy_dict[id_from_name(pk)]
        serializer = StrategySerializer(strategy)
        return Response(serializer.data)
