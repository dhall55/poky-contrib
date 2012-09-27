from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^operators/', include('hob.operators.urls')),
     url(r'^projects/', include('hob.projects.urls')),
     url(r'^groups/', include('hob.groups.urls')),
     url(r'^builds/', include('hob.builds.urls')),
)