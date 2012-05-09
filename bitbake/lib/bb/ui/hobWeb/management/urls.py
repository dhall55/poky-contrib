from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^login/', 'management.views.login'),
    url(r'^add_server/', 'management.views.add_server'),
    url(r'^del_server/', 'management.views.del_server'),
    url(r'^saveorupdate_server/', 'management.views.saveOrupdate_server'),
    url(r'^serverlist_disp/', 'management.views.serverlist_disp'),
    url(r'^userlist_disp/', 'management.views.userlist_disp'),
    url(r'^del_operator/', 'management.views.del_user'),
    url(r'^user_server_mapping/', 'management.views.user_server_mapping'),
    url(r'user_successful_cfg/', 'management.views.user_successful_cfg'),
)
