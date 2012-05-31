from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'views.default'),
    url(r'^hob/',include('hob.urls')),
    url(r'^management/', include('management.urls')),
    url(r'^error/', 'views.error'),
    url(r'^logout/', 'views.logout'),
)