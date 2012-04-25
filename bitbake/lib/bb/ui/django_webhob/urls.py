from django.conf.urls.defaults import patterns, include, url
#
from django_webhob.controller import *
from django_webhob import settings

urlpatterns = patterns('',
    (r'^$',index),
    (r'^send_command_asynconfs$',send_command_asynconfs),
    (r'^send_command_parserecipe$',send_command_parserecipe),
    (r'^getAsynconfsEvents$',getAsynconfsEvents),
    (r'^getParseRecipeEvents$',getParseRecipeEvents),
    (r'^recipe_list_page',recipe_list_page),
    (r'^send_command_buildpackage',send_command_buildpackage),
    (r'^getBuildPackageEvents',getBuildPackageEvents),
    (r'^ajax_rcp_include',ajax_rcp_include),
    (r'^ajax_pkg_include',ajax_pkg_include),
    (r'^send_command_buildimage',send_command_buildimage),
    (r'^getBuildimageEvents',getBuildimageEvents),

    (r'^history_list',history_list),
    (r'^api',api),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT})
)
