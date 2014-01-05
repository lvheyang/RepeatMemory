from django.db import models
from django.contrib.auth.models import User


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
    wordAmount = models.BigIntegerField(default=0)

    runningTestNum = models.IntegerField(default=0)
    completeTestNum = models.IntegerField(default=0)
    cancelTestNum = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class WordGroup(models.Model):

    repository = models.ForeignKey(WordRepository)
    name = models.CharField(max_length=50)
    wordAmount = models.BigIntegerField(default=0)

    runningTestNum = models.IntegerField(default=0)
    completeTestNum = models.IntegerField(default=0)
    cancelTestNum = models.IntegerField(default=0)

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

    owner = models.ForeignKey(User)
    repository = models.ForeignKey(WordRepository)
    group = models.ForeignKey(WordGroup)
    wordNum = models.IntegerField()
    answerNum = models.IntegerField(default=0)
    correctNum = models.IntegerField(default=0)
    errorNum = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    POSITIVE = 0
    NEGATIVE = 1

    TEST_DIRECTIONS = (
        (POSITIVE, "src to tar"),
        (NEGATIVE, "tar to src")
    )

    direction = models.IntegerField(choices=TEST_DIRECTIONS)

    RUNNING = 0
    COMPLETE = 1
    CANCEL = 2
    TEST_STATUS = (
        (RUNNING, 'running'),
        (COMPLETE, 'complete'),
        (CANCEL, 'cancel'),
    )
    status = models.IntegerField(choices=TEST_STATUS)

    def __unicode__(self):
        return self.group.repository.name + ":" + self.group.name


class TestHistory(models.Model):

    test = models.ForeignKey(WordTest)
    word = models.ForeignKey(Word)
    answerTimes = models.IntegerField(default=0)

    RIGHT = 0
    WRONG = 1
    WAITING = 2
    WORD_STATUS = (
        (RIGHT, 'right'),
        (WRONG, 'wrong'),
        (WAITING, 'not answer'),
    )
    status = models.IntegerField(choices=WORD_STATUS)

    def __unicode__(self):
        return self.test.__unicode__() + ":" + self.word.srcWord 