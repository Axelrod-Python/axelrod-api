from rest_framework import serializers, viewsets
from rest_framework.response import Response
import axelrod as axl


class StrategySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    classifier = serializers.DictField()


class StrategyViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = StrategySerializer(axl.strategies, many=True)
        return Response(serializer.data)
