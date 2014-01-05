#coding:utf-8
from django.http import HttpResponse

from django.shortcuts import render
from RepeatMemory.settings import *
from WordTest.models import WordRepository
from WordTest.dao import *


def show_common(func):

    def decorator(*args, **kwargs):
        request = args[0]
        common_content = {
            "static_url": STATIC_URL,
            "host": HOST,
            "loginUrl": LOGIN_URL,
            "logoutUrl": LOGOUT_URL,
            "username": request.user.username
        }
        ret = func(*args, **kwargs)

        if isinstance(ret, HttpResponse) :
            return ret

        template = ret[0]
        special_content = ret[1]
        content = dict(common_content, **special_content)
        return render(request, template, content)

    return decorator


# def check_repo(func):
#
#     def decorator(*args, **kwargs):
#         request = args[0]
#         rid = args[1]
#         user = request.user
#         repo = getRepoById(int(rid))
#
#         content = {}
#
#         if repo is None:
#             content['error_msg'] = "该词库不存在"
#             return ERROR_TEMPLATE, content
#
#         if not userCanViewRepo(user, repo):
#             content['error_msg'] = "你无权查看此词库"
#             return ERROR_TEMPLATE, content
#
#         return func(*args, **kwargs)
#
#     return decorator
#
#
# def check_test(func):
#
#     def decorator(*args, **kwargs):
#         request = args[0]
#         tid = args[1]
#         user = request.user
#         test = WordTest.objects.filter(pk=int(tid)).first()
#
#         content = {}
#
#         if test is None:
#             content['error_msg'] = "该测试不存在"
#             return ERROR_TEMPLATE, content
#
#         if not userCanViewRepo(user, test):
#             content['error_msg'] = "你无权进行此测试"
#             return ERROR_TEMPLATE, content
#
#         return func(*args, **kwargs)
#
#     return decorator



