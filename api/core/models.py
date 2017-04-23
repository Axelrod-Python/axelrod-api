from rest_framework import serializers
from django.contrib.postgres.fields import JSONField
import axelrod as axl

from .utils import strategy_id

from django.db.models import (
    BooleanField,
    DateTimeField,
    CharField,
    IntegerField,
    ForeignKey,
    FloatField,
    Model,
    ManyToManyField,
    TextField,
)

strategies_index = {strategy_id(s): s for s in axl.strategies}
CHEATING_NAMES = [strategy.__name__ for strategy in axl.cheating_strategies]


class Game(Model):

    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3

    STATUS_CHOICES = (
        (PENDING, 'PENDING'),
        (RUNNING, 'RUNNING'),
        (SUCCESS, 'SUCCESS'),
        (FAILED, 'FAILED'),
    )

    # Fields
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    status = IntegerField(choices=STATUS_CHOICES, default=PENDING)
    results = JSONField()

    class Meta:
        managed = False


class Tournament(Model):

    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3

    STATUS_CHOICES = (
        (PENDING, 'PENDING'),
        (RUNNING, 'RUNNING'),
        (SUCCESS, 'SUCCESS'),
        (FAILED, 'FAILED'),
    )

    # Fields
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    status = IntegerField(choices=STATUS_CHOICES, default=PENDING)
    results = JSONField(null=True)
    definition = ForeignKey('TournamentDefinition')

    def run(self, strategies):
        tournament = axl.Tournament(strategies,
                                    turns=self.definition.turns,
                                    noise=self.definition.noise,
                                    repetitions=self.definition.repetitions,
                                    with_morality=self.definition.with_morality,
                                    )
        self.status = 1
        self.save()
        results = tournament.play()
        self.status = 2
        self.save()
        return results


class TournamentDefinition(Model):
    # Fields
    name = CharField(max_length=255)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    turns = IntegerField()
    repetitions = IntegerField()
    noise = FloatField()
    with_morality = BooleanField()
    player_list = ManyToManyField('InternalStrategy')


class Match(Model):

    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3

    STATUS_CHOICES = (
        (PENDING, 'PENDING'),
        (RUNNING, 'RUNNING'),
        (SUCCESS, 'SUCCESS'),
        (FAILED, 'FAILED'),
    )

    # Fields
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    status = IntegerField(choices=STATUS_CHOICES, default=PENDING)
    results = JSONField(null=True)
    definition = ForeignKey('MatchDefinition')

    def run(self, strategies):
        match = axl.Match(strategies,
                          turns=self.definition.turns,
                          noise=self.definition.noise)
        self.status = 1
        self.save()
        match.play()
        self.status = 2
        self.save()
        return match


class MatchDefinition(Model):
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    turns = IntegerField()
    noise = FloatField()
    player_list = ManyToManyField('InternalStrategy')


class MoranProcess(Model):

    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3

    STATUS_CHOICES = (
        (PENDING, 'PENDING'),
        (RUNNING, 'RUNNING'),
        (SUCCESS, 'SUCCESS'),
        (FAILED, 'FAILED'),
    )

    # Fields
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    status = IntegerField(choices=STATUS_CHOICES, default=PENDING)
    results = JSONField(null=True)
    definition = ForeignKey('MoranDefinition')

    def run(self, strategies):
        mp = axl.MoranProcess(strategies,
                              turns=self.definition.turns,
                              noise=self.definition.noise,
                              mode=self.definition.mode,
                              )
        self.status = 1
        self.save()
        mp.play()
        self.status = 2
        self.save()
        return mp


class MoranDefinition(Model):
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    turns = IntegerField()
    noise = FloatField()
    mode = CharField(max_length=2)
    player_list = ManyToManyField('InternalStrategy')


class InternalStrategy(Model):
    id = TextField(primary_key=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)


class Result(Model):
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    type = CharField(max_length=255)
    result = JSONField()
