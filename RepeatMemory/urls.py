from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',

    #admin
    url(r'^admin/', include(admin.site.urls)),

    # redirect to WordTest app
    url(r'^$', RedirectView.as_view(url='/beidanci/', permanent=False), name='index'),
    url(r'^beidanci/', include('WordTest.urls')),

    # user login logout
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/beidanci/'}),
)
