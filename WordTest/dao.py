from django.db import transaction
from WordTest.models import *


def getRepoById(rid):
    try:
        repo = WordRepository.objects.get(pk=rid)
        return repo
    except WordRepository.DoesNotExist:
        return None


def userCanViewRepo(user, repo):
    return user.id == repo.owner.id


def userCanEditRepo(user, repo):
    return user.id == repo.owner.id


def addWords(repository, wordfile):

    i = 0
    for line in wordfile:
        if i <= 0:
            i += 1
            continue
        parts = line.split(",")
        group_name = parts[0].strip()
        src_word = parts[1].strip()
        tar_word = parts[2].strip()
        if len(parts) == 3:
            tips = ""
        elif len(parts) == 4:
            tips = parts[3].strip()
        else:
            continue

        group = None
        try:
            group = WordGroup.objects.get(repository=repository, name=group_name)
        except WordGroup.DoesNotExist:
            group = WordGroup(repository=repository, name=group_name)
            group.save()

        if group is not None:
            word = Word(group=group, srcWord=src_word, tarWord=tar_word, tips=tips)
            with transaction.atomic():
                repository.wordAmount += 1
                group.wordAmount += 1
                group.save()
                word.save()
                repository.save()
