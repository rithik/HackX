"""All models for judging project.

There is only one Event i.e. hackathon for each instance of this project.
There might be many Organizations (e.g. sponsors, partners) that will be
judging. Every User (e.g. judge, admin) must belong to an Organization,
and every Prize must belong to an Organization. Many Teams will submit a
project to be judged. A Demo is an instance where a Judge evaluates a Team.
For each Demo, the Judge will give DemoScores based on Criteria that you,
as the organizer, defines. The Criteria are restricted to integer ranges, so
you have the option to define CriteriaLabels for each value in the range.
"""
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=100)
    organizers = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL)
    est_time_per_demo = models.DecimalField(max_digits=3, decimal_places=1, default=5)
    min_judges_per_team = models.IntegerField(default=1)
    max_judges_per_sponsor_category = models.IntegerField(default=99)
    time_limit = models.IntegerField(default=120)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=255)
    table = models.CharField(max_length=15, blank=True)
    members = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)
    is_anchor = models.BooleanField(default=False)

    def __str__(self):
        return 'Table {} - {}'.format(self.table, self.name)

class Category(models.Model):
    from users.models import User

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    number_winners = models.IntegerField(default=1)
    min_judges = models.IntegerField(
        default=1, help_text="The minimum number of judges a team should be seen by for this category")
    is_opt_in = models.BooleanField(default=False)
    submissions = models.ManyToManyField(
        Team, related_name='categories', blank=True)
    judges = models.ManyToManyField(
        User, related_name='categories', blank=True)

    def __str__(self):
        return '[{}] {}'.format(self.organization.name, self.name)

    class Meta:
        verbose_name_plural = "categories"


# class Criteria(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     min_score = models.IntegerField(default=1)
#     max_score = models.IntegerField(default=5)
#     weight = models.DecimalField(default=1, decimal_places=2, max_digits=4)

#     def __str__(self):
#         return self.name


# class CriteriaLabel(models.Model):
#     criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
#     score = models.IntegerField()
#     label = models.CharField(max_length=255)

#     def __str__(self):
#         return '[{} - {}] {}'.format(self.criteria.name, self.score, self.label)


class Demo(models.Model):
    from users.models import User

    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    raw_score = models.DecimalField(max_digits=9, decimal_places=5, default=0)
    norm_score = models.DecimalField(max_digits=9, decimal_places=5, default=0)

    completed = models.BooleanField(default=False)

    ui = models.IntegerField(        
        default=0,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )

    creativity = models.IntegerField(        
        default=0,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )

    functionality = models.IntegerField(        
        default=0,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )

    impact = models.IntegerField(        
        default=0,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )

    feasibility = models.IntegerField(        
        default=0,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )

    @property
    def is_for_judge_category(self):
        for category in self.team.categories.all():
            if category.organization.id == self.judge.organization.id:
                return True
        return False

    def __str__(self):
        return '{} - {}'.format(self.judge, self.team.name)


# class DemoScore(models.Model):
#     demo = models.ForeignKey(Demo, on_delete=models.CASCADE)
#     criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
#     value = models.IntegerField()

#     def __str__(self):
#         return '{} = {} - {}'.format(self.demo, self.criteria.name, self.value)
