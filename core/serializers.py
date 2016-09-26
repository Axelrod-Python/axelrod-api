from rest_framework import serializers
from rest_framework.reverse import reverse


def strategy_id(strategy):
    return strategy.name.lower().replace(' ', '')


class StrategySerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=200)
    description = serializers.SerializerMethodField()
    classifier = serializers.SerializerMethodField()

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

    def get_classifier(self, strategy):
        classifier = strategy.classifier
        if classifier['memory_depth'] == float('inf'):
            classifier['memory_depth'] = -1
        return classifier
