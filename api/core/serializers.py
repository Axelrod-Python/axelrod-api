from rest_framework import serializers
from rest_framework.reverse import reverse

from . import models


def strategy_id(strategy):
    return strategy.name.lower().replace(' ', '')


class StrategySerializer(serializers.Serializer):
    """
    Serialize an axelrod strategy object based on
    introspection into its class attributes
    """
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
        # float('inf') is not valid json
        if classifier['memory_depth'] == float('inf'):
            classifier['memory_depth'] = -1
        return classifier

    def get_params(self, strategy):
        params = strategy.init_params()
        # float('inf') is not valid json
        if 'memory_depth' in params and params['memory_depth'] == float('inf'):
            params['memory_depth'] = -1
        return params


class StringListField(serializers.ListField):
    child = serializers.CharField(trim_whitespace=True)


class TournamentSerializer(serializers.ModelSerializer):
    player_list = StringListField(min_length=2, max_length=None)

    class Meta:
        model = models.TournamentDefinition
        fields = ('name', 'created', 'last_updated', 'turns',
                  'repetitions', 'noise', 'with_morality', 'player_list')


class MatchSerializer(serializers.ModelSerializer):
    player_list = StringListField(min_length=2, max_length=2)

    class Meta:
        model = models.MatchDefinition
        fields = ('turns', 'noise', 'player_list')


class ResultsSerializer:
    """
    Serialize an axelrod ResultSet class into a dictionary by
    iterating over its __dict__ method.

    For complex objects (Game, State objects) more in depth serialization
    is required - these are handled in separate methods. For example the
    state_distribution_keys are
    """

    # TODO implement state_distribution serializations
    state_distribution_keys = [
        'state_distribution',
    ]

    # keys that have not been implemented
    ignore_keys = [
        'normalised_state_distribution',
        'state_to_action_distribution',
        'normalised_state_to_action_distribution',
        'game',
    ]

    # keys where the value is not json serializable
    invalid_keys = [
        'progress_bar'
    ]

    # keys we should not retrieve from __dict__ method
    exclude = state_distribution_keys + ignore_keys + invalid_keys

    def __init__(self, results):
        """
        Parameters
        ----------
            results: ResultSet:
                https://github.com/Axelrod-Python/Axelrod/blob/master/axelrod/result_set.py
        """
        response_object = self.serialize_state_distributions(results)
        for key, value in results.__dict__.items():
            if key not in self.exclude:
                response_object[key] = value
        # we mimic DRF serializer by setting data property instead of returning
        self.data = response_object

    def serialize_state_distributions(self, results):
        """
        Initialize the response_object dictionary and set in it a
        set of lists that contain serialized Counter objects

        Parameters
        ----------

            results: ResultSet
                results from a Tournament/Match
        """
        return {
            key: self.serialize_state_distribution(getattr(results, key))
            for key in self.state_distribution_keys
        }

    @staticmethod
    def serialize_state_distribution(state_distribution):
        """
        Iterate over a state distribution and serialize all of
        its Counter objects

        Parameters
        ----------

            state_distribution: list of Counter
                state_distribution from ResultSet
        """
        distribution = []
        for counter in state_distribution:
            distribution.append([c.most_common() for c in counter])
        return distribution
