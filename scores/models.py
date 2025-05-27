import uuid
from django.db import models
from django.core.exceptions import ValidationError


class TimestampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Competition(TimestampedModel):
    name = models.CharField(max_length=200)
    scope = models.CharField(max_length=100, null=True, blank=True)
    teams = models.ManyToManyField("Team", blank=True)

    def __str__(self):
        return self.name
    

class Team(TimestampedModel):
    logo = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=200)
    people = models.ManyToManyField("Person", blank=True)
    competitions = models.ManyToManyField(Competition, blank=True)

    def __str__(self):
        return self.name
    

class Person(TimestampedModel):
    given_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    family_name = models.CharField(max_length=200, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    teams = models.ManyToManyField(Team, blank=True)

    def __str__(self):
        return f'{self.given_name} {self.family_name}'
    

class Role(TimestampedModel):
    name = models.CharField(max_length=200)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    match = models.ForeignKey("Match", on_delete=models.PROTECT)


class Match(TimestampedModel):
    match_date = models.DateTimeField(null=True, blank=True)
    first_team = models.ForeignKey(Team, on_delete=models.PROTECT, 
                                   related_name='matches_home', 
                                   null=True, blank=True)
    second_team = models.ForeignKey(Team, on_delete=models.PROTECT,
                                    related_name='matches_away', 
                                    null=True, blank=True)
    STATUS_CHOICES = [
        ('to_be_scheduled', 'To Be Scheduled'),
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('finished', 'Finished'),
        ('postponed', 'Postponed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_be_scheduled', 
                              null=True,
                              blank=True)
    first_team_goals_scored = models.IntegerField(null=True, blank=True)
    second_team_goals_scored = models.IntegerField(null=True, blank=True)

    def clean(self):
        super().clean()
        if self.first_team == self.second_team:
            raise ValidationError({'__all__': "Teams must be different."})
        if self.status == 'to_be_scheduled' and self.match_date != None:
            raise ValidationError({'__all__': "'Match date' - 'To Be Scheduled' conflict. Those are mutually exlusive."})
            

    def __str__(self):
        if self.status == 'to_be_scheduled':
            date_detail = 'To Be Scheduled'
        else:
            date_detail = self.match_date
        return f'{self.first_team.name} - {self.second_team.name} ({date_detail})'

class InMatchEvent(TimestampedModel):
    EVENT_TYPE_CHOICES = [
        ('card', 'Card'),
        ('entry', 'Entry'),
        ('exit', 'Exit'),
        ('goal', 'Goal'),
    ]
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    match = models.ForeignKey(Match, on_delete=models.PROTECT, null=True, blank=True, related_name='events')
    minute = models.IntegerField(null=True, blank=True)
    detail = models.CharField(max_length=250, null=True, blank=True)
    
    # Optional fields for specific event types
    # Card fields
    color = models.CharField(
        max_length=10,
        choices=[('yellow', 'Yellow'), ('red', 'Red')],
        null=True,
        blank=True,
        help_text="Only applicable if event_type is 'card'."
    )
    # Entry/Exit fields
    other_player = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+',
        help_text="Only applicable if event_type is 'entry' or 'exit'."
    )
    # Goal fields
    goal_type = models.CharField(
        max_length=10,
        choices=[
            ('penalty', 'Penalty'),
            ('freekick', 'Freekick'),
            ('open_play', 'Open Play'),
            ('own_goal', 'Own Goal'),
        ],
        null=True,
        blank=True,
        help_text="Only applicable if event_type is 'goal'."
    )

    def clean(self):
        super().clean()
        # Example: Validations to ensure relevant fields are provided based on event_type.
        if self.event_type == 'card' and not self.color:
            raise ValidationError({'color': "A card event must have a color."})
        if self.event_type in ['entry', 'exit'] and not self.other_player:
            raise ValidationError({'other_player': "This event requires an other player."})
        if self.event_type == 'goal' and not self.goal_type:
            raise ValidationError({'goal_type': "A goal event must have a goal type."})