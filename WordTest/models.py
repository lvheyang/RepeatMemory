from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Languages(models.Model):

    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class WordRepository(models.Model):

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    createTime = models.DateTimeField(auto_now_add=True)
    info = models.TextField()
    srcLang = models.ForeignKey(Languages, related_name="src_language")
    tarLang = models.ForeignKey(Languages, related_name="target_language")

    def __unicode__(self):
        return self.name


class WordGroup(models.Model):

    repository = models.ForeignKey(WordRepository)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Word(models.Model):

    group = models.ForeignKey(WordGroup)
    srcWord = models.CharField(max_length=200)
    tarWord = models.CharField(max_length=200)
    tips = models.TextField()

    def __unicode__(self):
        return self.srcWord


class WordTest(models.Model):

    repository = models.ForeignKey(WordRepository)
    group = models.ForeignKey(WordGroup)
    completeNum = models.IntegerField(default=0)
    sumNum = models.IntegerField(default=0)
    correctNum = models.IntegerField(default=0)
    errorNum = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)

