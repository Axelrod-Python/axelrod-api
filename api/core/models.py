from django.contrib.postgres.fields import JSONField
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
import axelrod as axl


class Contest(Model):

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

    class Meta:
        abstract = True


class ContestDefinition(Model):
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    turns = IntegerField()
    noise = FloatField()
    player_list = ManyToManyField('InternalStrategy')

    class Meta:
        abstract = True


class Tournament(Contest):

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


class TournamentDefinition(ContestDefinition):
    repetitions = IntegerField()
    with_morality = BooleanField()


class Match(Contest):

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


class MatchDefinition(ContestDefinition):

    class Meta:
        managed = True


class MoranProcess(Contest):

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


class MoranDefinition(ContestDefinition):
    mode = CharField(max_length=2)


class InternalStrategy(Model):
    """
    This model is used to represent strategies in an internal
    database table. Contests reference this in a ManyToMany
    to store the strategies in their player_list field. This is
    necessary to facilitate normalization of the database.
    """
    id = TextField(primary_key=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)


