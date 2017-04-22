from rest_framework import serializers
from django.contrib.postgres.fields import JSONField
from django.db.models import (
    BooleanField,
    DateTimeField,
    CharField,
    IntegerField,
    TextField,
    FloatField,
    Model,
)
import axelrod


CHEATING_NAMES = [strategy.__name__ for strategy in axelrod.cheating_strategies]

# class Tournament(Model):

#     PENDING = 0
#     RUNNING = 1
#     SUCCESS = 2
#     FAILED = 3

#     STATUS_CHOICES = (
#         (PENDING, 'PENDING'),
#         (RUNNING, 'RUNNING'),
#         (SUCCESS, 'SUCCESS'),
#         (FAILED, 'FAILED'),
#     )

#     # Fields
#     created = DateTimeField(auto_now_add=True, editable=False)
#     last_updated = DateTimeField(auto_now=True, editable=False)
#     status = IntegerField(choices=STATUS_CHOICES, default=PENDING)
#     results = JSONField()


#     class Meta:
#         ordering = ('-created',)

#     def __unicode__(self):
#         return u'%s' % self.id

#     def get_absolute_url(self):
#         return reverse('core_tournament_detail', args=(self.id,))

#     def get_update_url(self):
#         return reverse('core_tournament_update', args=(self.id,))

#     def get_results_url(self):
#         return reverse('core_tournament_results', args=(self.id,))

#     def to_json(self):
#         json_results = []
#         if self.results:
#             for (player, scores) in self.results:
#                 json_results.append({"player": player, "scores": scores})

#         json_results = {
#             "results": json_results,
#             "meta": {
#                 "definition": self.tournament_definition.to_json(),
#                 "cheating_strategies": CHEATING_NAMES
#             }
#         }

#         return json_results

#     def run(self):

#         if self.status != Tournament.PENDING:
#             raise Exception(
#                 u'[tournament %d, current status: %s] SKIPPED !' % (
#                     self.id, self.get_status_display()))

#         try:
#             self.status = Tournament.RUNNING
#             self.save(update_fields=['status', ])

#             start = datetime.now()

#             players = json.loads(self.tournament_definition.players)

#             strategies = []
#             for strategy_str, number_of_players in players.items():
#                 for i in range(0, int(number_of_players or 0)):
#                     strategies.append(getattr(axelrod, strategy_str)())

#             tournament_runner = axelrod.Tournament(
#                 players=strategies,
#                 turns=self.tournament_definition.turns,
#                 repetitions=self.tournament_definition.repetitions,
#                 noise=self.tournament_definition.noise)
#             result_set = tournament_runner.play()

#             self.results = []
#             for rank in result_set.ranking:
#                 player = tournament_runner.players[rank].name
#                 scores = result_set.normalised_scores[rank]
#                 self.results.append((player, scores))

#             end = datetime.now()
#             duration = (end - start).seconds

#             # TODO: save duration
#             # self.duration = duration
#             self.status = Tournament.SUCCESS
#             self.save(update_fields=['status', 'results'])

#         except Exception as e:
#             # log errors and set tournament status to aborted
#             self.status = Tournament.FAILED
#             self.save(update_fields=['status', ])
#             # TODO: eventually save error message in model


class TournamentDefinition(Model):
    # Fields
    name = CharField(max_length=255)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
    turns = IntegerField()
    repetitions = IntegerField()
    noise = FloatField()
    with_morality = BooleanField()
    # Relationship Fields
    # tournament = ForeignKey('Tournament',)


class MatchDefinition(Model):
    turns = IntegerField()
    noise = FloatField()
