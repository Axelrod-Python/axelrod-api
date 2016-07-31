from rest_framework import serializers, viewsets
from rest_framework.response import Response
import axelrod as axl


class StrategySerializer(serializers.Serializer):
    class Meta:
        fields = ('name',)

    name = serializers.CharField(max_length=200)


class StrategyViewSet(viewsets.ViewSet):

    def list(self, request):
        serializer = StrategySerializer(axl.all_strategies, many=True)
        return Response(serializer.data)
