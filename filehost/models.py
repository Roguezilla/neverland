from django.db import models

class File(models.Model):
    uploader = models.CharField(max_length=256)
    filename = models.CharField(max_length=256)
    path = models.CharField(max_length=256)
    size = models.CharField(max_length=256)