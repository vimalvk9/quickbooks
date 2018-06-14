'''
All database models here for records app
'''
from __future__ import unicode_literals
import datetime
from django.contrib.auth.models import User
from django.db import models



class YellowUserToken(models.Model):
    """
        Parent table for the database(contains the primary key).
    """
    user = models.IntegerField()
    yellowant_token = models.CharField(max_length=100)
    yellowant_id = models.IntegerField(default=0)
    yellowant_integration_invoke_name = models.CharField(max_length=100)
    yellowant_integration_id = models.IntegerField(default=0)
    webhook_id = models.CharField(max_length=100, default="")
    webhook_last_updated = models.DateTimeField(default=datetime.datetime.utcnow)
    realmId = models.CharField(max_length=512, default="")

class YellowAntRedirectState(models.Model):
    """
        Child table
    """
    user = models.IntegerField()
    state = models.CharField(max_length=512, null=False)

class AppRedirectState(models.Model):
    """
        Child table
    """
    user_integration = models.ForeignKey(YellowUserToken, on_delete=models.CASCADE)
    state = models.CharField(max_length=512, null=False)

class QuickbookUserToken(models.Model):
    """
        Child table
    """
    user_integration = models.ForeignKey(YellowUserToken, on_delete=models.CASCADE)
    refreshExpiry = models.IntegerField()
    accessToken = models.CharField(max_length=32768, null=False)
    tokenType = models.CharField(max_length=512, null=False)
    refreshToken = models.CharField(max_length=512, null=False)
    accessTokenExpiry = models.IntegerField()
    login_update_flag = models.BooleanField(default=False, max_length=100)
    realmId = models.CharField(default="", max_length=512, null=False)
class QuickUserDetails(models.Model):
    user_integration = models.ForeignKey(QuickbookUserToken, on_delete=models.CASCADE)
    realmId = models.CharField(max_length=512,null=False)


