from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^register/', 'hob.operators.views.register'),
     url(r'^save_user/', 'hob.operators.views.save_user'),
     url(r'^login/', 'hob.operators.views.login'),
     url(r'^logout/', 'hob.operators.views.logout'),
     url(r'^error/', 'hob.operators.views.error'),
)