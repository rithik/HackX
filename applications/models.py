from django.db import models
from users.models import User

class Application(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    first_name = models.CharField(max_length=1000, default="")
    last_name = models.CharField(max_length=1000, default="")
    
    school = models.CharField(max_length=1000, default="")
    grad_year = models.IntegerField(default=0)
    gender = models.CharField(max_length=100, default="")
    race = models.CharField(max_length=100, default="")
    describe = models.CharField(max_length=200, default="")
    why = models.CharField(max_length=1800, default="")
    major = models.CharField(max_length=1000, default="")

    birthday = models.CharField(max_length=1000, default="")
    mlh_rules = models.BooleanField(default=False)
    mlh_consent = models.BooleanField(default=False)
    hackathons = models.IntegerField(default=0)
    app_complete = models.BooleanField(default=False)
    
    referrer = models.CharField(max_length=100, default="")
    referrer_locked = models.BooleanField(default=False)

    travel = models.BooleanField(default=False)
    where_from = models.CharField(max_length=1000, default="")
    travel_method = models.CharField(max_length=1000, default="")
    miles = models.CharField(max_length=100, default="")
    cost = models.CharField(max_length=1000, default="")

    accepted = models.BooleanField(default=False)
    waitlisted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return  "Application - {}".format(self.user)

class Confirmation(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    tshirt = models.CharField(max_length=1000, default="")
    dietary = models.CharField(max_length=1000, default="")
    phone = models.CharField(max_length=100, default="")
    carrier = models.CharField(max_length=100, default="Other")
    github = models.CharField(max_length=1000, default="")
    notes = models.CharField(max_length=10000, default="")
    resume_file_name = models.CharField(max_length=10000, default="")
    discord_id = models.CharField(max_length=100, default="")

    confirmed = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    
    def __str__(self):
        return  "Confirmation: {}".format(self.user)
        
class TshirtOrder(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="tshirt_order"
    )

    tshirt = models.CharField(max_length=10, default="")
    street_address = models.CharField(max_length=200, default="")
    city = models.CharField(max_length=100, default="")
    state = models.CharField(max_length=100, default="")
    country = models.CharField(max_length=100, default="")
    zip_code = models.CharField(max_length=10, default="")
    devpost_url = models.URLField()
    devpost_email = models.EmailField(max_length=100, default="")
    
    @property
    def is_valid_url(self):
        from judging.models import Team
        t = Team.objects.filter(link=self.devpost_url).count()
        if t > 0:
            return True
        return False

    def __str__(self):
        return "TshirtShipping: {}".format(self.user)
