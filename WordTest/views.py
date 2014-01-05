#coding:utf-8
from random import randint

import json
import re

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from WordTest.models import *
from WordTest.decorators import *
from WordTest.dao import *

@login_required
@show_common
def index(request):
    user = request.user
    content = {
        'label': '词库',
        'languages': [],
        'repos': [],
    }
    all_langs = Languages.objects.all()
    for lang in all_langs:
        content['languages'].append({"id": lang.id, "name": lang.name})

    all_repos = WordRepository.objects.filter(owner=user)
    for r in all_repos:
        repo = {
            'name': r.name ,
            'num': r.wordAmount,
            'id': r.id,
        }
        if r.runningTestNum > 0:
            repo['notification'] = r.runningTestNum

        content['repos'].append(repo)

    template = "index.html"
    return template, content


@login_required
def createRepository(request):

    owner = request.user
    name = request.POST.get('repoName', "")
    info = request.POST.get('info', "")
    word_file = request.FILES.get('repoFile')

    src = request.POST['srclang']
    tar = request.POST['tarlang']

    src_lang = Languages.objects.get(pk=src)
    tar_lang = Languages.objects.get(pk=tar)

    repo = WordRepository(name=name, owner=owner, info=info, srcLang=src_lang, tarLang=tar_lang)
    repo.save()
    addWords(repo, word_file)

    return HttpResponseRedirect('/beidanci/')


@login_required
@show_common
def viewRepository(request, rid):

    user = request.user
    content = {
        "label": "查看词库",
        'languages': [],
        'repo': {},
        'groups': [],
        'directions': {}
    }

    repo = getRepoById(int(rid))

    if repo is None:
        content['error_msg'] = "该词库不存在"
        return ERROR_TEMPLATE, content

    if not userCanViewRepo(user, repo):
        content['error_msg'] = "你无权查看此词库"
        return ERROR_TEMPLATE, content

    src_lang = repo.srcLang
    tar_lang = repo.tarLang
    all_langs = Languages.objects.all()
    for lang in all_langs:
        l = {"id": lang.id, "name": lang.name}
        if src_lang.id == lang.id:
            l['isSrc'] = True
        if tar_lang.id == lang.id:
            l['isTar'] = True
        content['languages'].append(l)

    content['repo']['id'] = repo.id
    content['repo']['name'] = repo.name
    content['repo']['info'] = repo.info
    content['repo']['createTime'] = repo.createTime.strftime("%Y-%m-%d %H:%M:%S")
    content['repo']['wordAmount'] = repo.wordAmount
    content['repo']['runningTestNum'] = repo.runningTestNum
    content['repo']['completeTestNum'] = repo.completeTestNum
    content['repo']['cancelTestNum'] = repo.cancelTestNum
    content['repo']['srcLang'] = {"id": src_lang.id, "name": src_lang.name}
    content['repo']['tarLang'] = {"id": tar_lang.id, "name": tar_lang.name}

    last_running_test = WordTest.objects.filter(repository=repo, status=WordTest.RUNNING)
    if len(last_running_test) > 0:
        content['last_running_test_id'] = last_running_test.order_by("-id").first().id

    groups = WordGroup.objects.filter(repository=repo)
    for g in groups:
        content['groups'].append({"id": g.id, "name": g.name})

    content['directions'] = {'positive': WordTest.POSITIVE, 'negative':WordTest.NEGATIVE}

    if userCanEditRepo(user, repo):
        content['editable'] = True
    else:
        content['editable'] = False

    template = "view-repo.html"
    return template, content


@login_required
@show_common
def runTest(request, tid):

    user = request.user
    test = WordTest.objects.filter(pk=int(tid)).first()

    content = {
        "label": "测试中...",
        "test": {},
        "repo": {},
    }

    if test is None:
        content['error_msg'] = "该测试不存在"
        return ERROR_TEMPLATE, content

    if not userCanViewRepo(user, test):
        content['error_msg'] = "你无权进行此测试"
        return ERROR_TEMPLATE, content

    questions = TestHistory.objects.filter(
        Q(test=test), Q(status=TestHistory.WAITING) | Q(status=TestHistory.WRONG))
    num = len(questions)

    group = test.group
    repo = group.repository

    if num <= 0:
        try:
            with transaction.atomic():
                test.status = WordTest.COMPLETE
                test.save()
                group.runningTestNum -= 1
                group.completeTestNum += 1
                group.save()
                repo.completeTestNum += 1
                repo.runningTestNum -= 1
                repo.save()
        except Exception:
            content['error_msg'] = "测试异常终止"
            return ERROR_TEMPLATE, content

        return HttpResponseRedirect('/beidanci/test/success/')

    random_index = randint(0, num-1)

    content['repo']['name'] = repo.name
    content['repo']['group'] = group.name
    content['test']['id'] = test.id
    content['test']['srcLang'] = repo.srcLang.name if test.direction == WordTest.POSITIVE else repo.tarLang.name
    content['test']['tarLang'] = repo.tarLang.name if test.direction == WordTest.POSITIVE else repo.srcLang.name
    content['test']['wordNum'] = test.wordNum
    content['test']['answerNum'] = test.answerNum
    content['test']['correctNum'] = test.correctNum
    content['test']['errorNum'] = test.errorNum

    test_history  = questions[random_index]
    qword = test_history.word
    content['question'] = qword.srcWord if test.direction == WordTest.POSITIVE else qword.tarWord
    content['tips'] = qword.tips
    content['test_history_id'] = test_history.id


    return "test.html", content


@login_required
@show_common
def submitAnswer(request, tid):

    user = request.user
    test = WordTest.objects.filter(pk=int(tid)).first()

    content = {
        "label": "测试中...",
    }

    if test is None:
        content['error_msg'] = "该测试不存在"
        return ERROR_TEMPLATE, content

    if not userCanViewRepo(user, test):
        content['error_msg'] = "你无权进行此测试"
        return ERROR_TEMPLATE, content

    direction = test.direction
    test_record_id = request.POST['testRecordId'].strip()

    pattern = re.compile(r"^\d+$")
    if not pattern.match(test_record_id):
        content['error_msg'] = "测试id格式不对"
        return ERROR_TEMPLATE, content

    answer = request.POST['answer'].strip()
    test_record = TestHistory.objects.filter(pk=int(test_record_id)).first()
    word = test_record.word

    if direction == WordTest.POSITIVE:
        right_answer = word.tarWord.strip()
    else:
        right_answer = word.srcWord.strip()

    ret = {
        'submitSuccess': True,
    }
    if answer == right_answer:
        ret['answerRight'] = True
    else:
        ret['answerRight'] = False
    ret['answer'] = right_answer

    try:
        with transaction.atomic():
            test_record.status = TestHistory.RIGHT if ret['answerRight'] else TestHistory.WRONG
            test_record.save()
            test.answerNum += 1
            if ret['answerRight']:
                test.correctNum += 1
            else:
                test.errorNum += 1
            test.save()
    except :
        ret['submitSuccess'] = False

    return HttpResponse(json.dumps(ret), mimetype='application/javascript')


@login_required
@show_common
def createTest(request, rid):

    user = request.user
    repo = getRepoById(int(rid))

    content = {
        "label": "创建词库"
    }

    if repo is None:
        content['error_msg'] = "该词库不存在"
        return ERROR_TEMPLATE, content

    if not userCanViewRepo(user, repo):
        content['error_msg'] = "你无权查看此词库"
        return ERROR_TEMPLATE, content

    direction = request.POST['translateDirection']
    groupId = request.POST['group']

    pattern = re.compile(r'^\d+$')
    if not (pattern.match(direction) and pattern.match(groupId)):
        content['error_msg'] = "语言或者群组格式不正确"
        return ERROR_TEMPLATE, content

    direction = int(direction)
    groupId = int(groupId)

    group = WordGroup.objects.filter(pk=groupId).first()
    if group is None:
        content['error_msg'] = "测试群组不存在"
        return ERROR_TEMPLATE, content

    test = None
    try:
        with transaction.atomic():
            words = Word.objects.filter(group=group)
            test = WordTest(owner=user, group=group,
                            wordNum=len(words), direction=direction,
                            status=WordTest.RUNNING, repository=repo)
            test.save()
            group.runningTestNum += 1
            group.save()
            repo.runningTestNum += 1
            repo.save()
            for word in words:
                item = TestHistory(test=test, word=word, status=TestHistory.WAITING)
                item.save()
    except Exception:
        content['error_msg'] = "创建测试失败"
        return ERROR_TEMPLATE, content

    return HttpResponseRedirect("/beidanci/test/run/" + str(test.id))






