from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^admin_login/', 'management.views.admin_login'),
     url(r'^login/', 'management.views.login'),
     url(r'^manage_list/', 'management.views.manage_list'),
     url(r'^disp_UserList/', 'management.views.disp_UserList'),
     url(r'^update_userInfo/', 'management.views.update_userInfo'),
     url(r'^save_userInfo/', 'management.views.save_userInfo'),
     url(r'^remove_users/', 'management.views.remove_users'),
     url(r'^disp_BitbakeList/', 'management.views.disp_BitbakeList'),
     url(r'^saveOrupdate_bitbake/', 'management.views.bitbakeInfo'),
     url(r'^save_bitbake/', 'management.views.save_bitbake'),
     url(r'^remove_bitbakes/', 'management.views.remove_bitbakes'),
     url(r'^disp_BitbakeAndUserMapping/', 'management.views.disp_BitbakeAndUserMapping'),
     url(r'^disp_BuildConfig/', 'management.views.disp_BuildConfig'),
     url(r'^remove_BuildConfig/', 'management.views.remove_BuildConfig'),
     url(r'^disp_Logs/', 'management.views.disp_logs'),
)