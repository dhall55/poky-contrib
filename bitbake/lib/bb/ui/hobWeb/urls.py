from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'hob.views.login'),
    url(r'^hob/',include('hob.urls')),
    url(r'^administrator/', include('management.urls')),
    url(r'^login/', 'views.login'),
    url(r'^register/','views.register'),
    url(r'^logout/','views.logout'),
    url(r'^invalid/','views.logerror'),
)
