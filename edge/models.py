from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    grad_year = models.PositiveIntegerField()

    def __str__(self):
        return self.first_name + " " + self.last_name

class Pitch(models.Model):
    title = models.CharField(max_length=200)
    stock_exchange_abbreviation = models.CharField(max_length=30, default="NYSE")
    stock_ticker = models.CharField(max_length=30, default="AAPL")
    pitch_date = models.DateField("date pitched")
    pitchers = models.ManyToManyField(Member)
    vote_count_for = models.PositiveIntegerField(default=0)
    vote_count_against = models.PositiveIntegerField(default=0)
    investment_strategy = models.CharField(max_length=4, choices=[("RV", "Relative Value"), ("SSG", "Special Situations"), ("GM", "Global Macro"), ("Risk", "Risk")], default="RV")
    investment_entered = models.BooleanField(default=False)
    pitch_price = models.FloatField(default=0.0)
    entry_date = models.DateField(null=True, blank=True)
    entry_price = models.FloatField(null=True, blank=True)
    currently_invested = models.BooleanField(default=False)
    theses_for_investment = models.TextField(default="No Theses")
    misperceptions = models.TextField(default="No Misperceptions")
    major_concerns = models.TextField(default="No Major Concerns")
    reasons_for_weight = models.TextField(default="No Reasons for Weight")
    key_signposts = models.TextField(default="No Key Signposts")
    catalysts = models.TextField(default="No Catalysts")
    threats_downsides = models.TextField(default="No Threats")
    other_notes = models.TextField(default="No Other Notes")

    def __str__(self):
        return self.title