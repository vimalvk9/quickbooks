# -*- coding: utf-8 -*-

import datetime
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Bearer:
    """
        Child table
    """
    def __init__(self, refreshExpiry, accessToken, tokenType, refreshToken, accessTokenExpiry, idToken=None):
        self.refreshExpiry = refreshExpiry
        self.accessToken = accessToken
        self.tokenType = tokenType
        self.refreshToken = refreshToken
        self.accessTokenExpiry = accessTokenExpiry
        self.idToken = idToken
