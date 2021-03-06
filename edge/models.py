from django.db import models
from aifedge.storage_backends import PublicFileStorage, PrivateDataStorage
import datetime as datetime
from pytz import timezone

class Member(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    grad_year = models.PositiveIntegerField()

    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + str(self.grad_year) + ")"

class Pitch(models.Model):
    title = models.CharField(max_length=200)
    long_investment = models.BooleanField(default=False)
    stock_exchange_abbreviation = models.CharField('Stock Exchange Abbreviation', max_length=30, default="NYSE")
    stock_ticker = models.CharField(max_length=30, default="AAPL")
    pitch_date = models.DateField("Date Pitched")
    pitchers = models.ManyToManyField(Member)
    vote_count_for = models.PositiveIntegerField(default=0)
    vote_count_against = models.PositiveIntegerField(default=0)
    investment_strategy = models.CharField(max_length=4, choices=[("RV", "Relative Value"), ("SSG", "Special Situations"), ("GM", "Global Macro"), ("Risk", "Risk")], default="RV")
    investment_entered = models.BooleanField(default=False)
    pitch_price = models.FloatField(default=0.0)
    target_price = models.FloatField(null=True, blank=True, default=0.0,)
    entry_date = models.DateField(null=True, blank=True)
    entry_price = models.FloatField(null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)
    exit_price = models.FloatField(null=True, blank=True)
    currently_invested = models.BooleanField(default=False)
    theses_for_investment = models.TextField(default="No Theses")
    misperceptions = models.TextField(default="No Misperceptions")
    major_concerns = models.TextField(default="No Major Concerns")
    catalysts = models.TextField(default="No Catalysts")
    key_signposts = models.TextField(default="No Key Signposts")
    reasons_for_weight = models.TextField(default="No Reasons for Weight")
    threats_downsides = models.TextField(default="No Threats")
    other_notes = models.TextField(default="No Other Notes")
    exit_notes = models.TextField(null=True, blank=True, default="No Exit Notes")
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Pitches"

class Document(models.Model):
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, default=None)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True)
    upload = models.FileField(default=None, storage=PublicFileStorage())

    def __str__(self):
        return self.upload.name

def rename_data_file(instance, filename):
    filename = "data_" + datetime.datetime.now(timezone('US/Eastern')).strftime('%m%d%Y') + ".csv"
    return filename

class DataFile(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True)
    # upload = models.FileField(storage=PrivateDataStorage())
    upload = models.FileField(upload_to=rename_data_file, storage=PrivateDataStorage())

    def __str__(self):
        return self.upload.name

class Tool(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(default="No Description")
    creators = models.ManyToManyField(Member)
    template_name = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.title

