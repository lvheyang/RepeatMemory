from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^$', 'WordTest.views.index', name='index'),
    url(r'^repo/create/$', 'WordTest.views.createRepository', name='createRepo'),
    url(r'^repo/view/(\d+)/', 'WordTest.views.viewRepository', name='viewRepo'),
    url(r'^test/new/(\d+)/', 'WordTest.views.createTest', name='newTest'),
    url(r'^test/run/(\d+)/', 'WordTest.views.runTest', name='runTest'),
    url(r'^test/submit/(\d+)/', 'WordTest.views.submitAnswer', name='submitAnswer')
)


