import inspect
import json
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.response import Response

from . import models


def strategy_id(strategy):
    return strategy.name.lower().replace(' ', '')


class StrategySerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=200)
    description = serializers.SerializerMethodField()
    classifier = serializers.SerializerMethodField()
    params = serializers.SerializerMethodField()

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

    def get_params(self, strategy):
        params = strategy.init_params()
        if 'memory_depth' in params and params['memory_depth'] == float('inf'):
            params['memory_depth'] = -1
        return params


class TournamentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TournamentDefinition
        fields = ('name', 'created', 'last_updated', 'turns',
                  'repetitions', 'noise', 'with_morality', 'players')


class MatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MatchDefinition
        fields = ('turns', 'noise', 'players')


class ResultsSerializer:

    data = None

    def __init__(self, results):
        results_object = self.serialize_state_distributions(results)
        for key, value in results.__dict__.items():
            try:
                json.dumps(key)
                json.dumps(value)
                results_object[key] = value
            except TypeError:
                pass
        self.data = results_object

    def serialize_state_distributions(self, results):
        keys = [
            'state_distribution',
            'normalised_state_distribution',
            'state_to_action_distribution',
            'normalised_state_to_action_distribution'
        ]
        return {
            key: self.serialize_state_distribution(getattr(results, key))
            for key in keys
        }

    def serialize_state_distribution(self, state_distribution):
        distribution = []
        for row in state_distribution:
            distribution.append([c.most_common() for c in row])
        return distribution
