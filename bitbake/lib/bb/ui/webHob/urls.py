from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^$', 'views.index'),
     url(r'^hob/', include('hob.urls')),
     url(r'^admin_login/', 'views.admin_login'),
     url(r'^admin_index/', 'views.admin_index'),
     url(r'^edit_bitbake/', 'views.edit_bitbake'),
     url(r'^delete_bitbake/', 'views.delete_bitbake'),
     url(r'^reset_bitbake_all/', 'views.reset_bitbake_all'),
     url(r'^connect_bitbake/', 'views.connect_bitbake'),
     url(r'^install/','views.index_install'),
     url(r'^cmd_install/','views.cmd_install'),
     url(r'^get_install_log/','views.get_install_log'),
     url(r'^cmd_start/','views.cmd_start'),
     url(r'^get_start_log/','views.get_start_log'),
     url(r'^stop/','views.stop'),
     url(r'^status/','views.status'),
)
