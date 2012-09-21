from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^index/', 'hob.groups.views.index'),
     url(r'^save_group/', 'hob.groups.views.save_group'),
     url(r'^add_someone_to_group/', 'hob.groups.views.add_someone_to_group'),
     url(r'^set_group_permission/', 'hob.groups.views.set_group_permission'),
     url(r'^get_user_permission/', 'hob.groups.views.get_user_permission'),
     url(r'^delete_memeber_from_group/', 'hob.groups.views.delete_memeber_from_group'),
     url(r'^set_project_group_permission/', 'hob.groups.views.set_project_group_permission'),
     url(r'^get_project_user_permission/', 'hob.groups.views.get_project_user_permission'),
)