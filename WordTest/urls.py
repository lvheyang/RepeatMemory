from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

    url(r'^$', 'WordTest.views.index', name='index'),
)


