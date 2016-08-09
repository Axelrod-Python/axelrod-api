from rest_framework import serializers, viewsets
from rest_framework.response import Response
import axelrod as axl


class StrategySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.SerializerMethodField()
    classifier = serializers.DictField()

    def get_description(self, strategy):
        return strategy.__doc__


class StrategyViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = StrategySerializer(axl.strategies, many=True)
        return Response(serializer.data)
