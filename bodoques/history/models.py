from django.db import models

class Site(models.Model):
    url = models.CharField(max_length=255, db_index=True, unique=True)
    title = models.CharField(max_length=255)
    score = models.IntegerField(default=-1)
    
class User(models.Model):
    uid = models.CharField(max_length=255, db_index=True, unique=True)
    name = models.CharField(max_length=255)
    allowed_time = models.IntegerField(default=100000)
    
class Activity(models.Model):
    user = models.ForeignKey(User, db_index=True)
    site = models.ForeignKey(Site, db_index=True)
    datetime = models.DateTimeField(auto_now=True)
    seconds = models.IntegerField()
    
class TimeGrant(models.Model):
    user = models.ForeignKey(User, db_index=True)
    datetime = models.DateTimeField(auto_now=True)
    seconds = models.IntegerField()