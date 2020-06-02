from django.db import models

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

class Document(models.Model):
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, default=None)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True)
    upload = models.FileField(default=None)

    def __str__(self):
        return self.upload.name


# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')


# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
    
