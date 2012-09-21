from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^index/', 'hob.projects.views.index'),
     url(r'^save_project/', 'hob.projects.views.save_project'),
     url(r'^projects_myproject/', 'hob.projects.views.projects_myproject'),
     url(r'^add_someone_to_project/', 'hob.projects.views.add_someone_to_project'),
     url(r'^add_mygroup_to_project/', 'hob.projects.views.add_mygroup_to_project'),
     url(r'^projects_history/', 'hob.projects.views.projects_history'),
     url(r'^projects_settings/', 'hob.projects.views.projects_settings'),
     url(r'^projects_permisisons/', 'hob.projects.views.projects_permisisons'),
     url(r'^save_advance_settings/', 'hob.projects.views.save_advance_settings'),
     url(r'^check_project_config/', 'hob.projects.views.check_project_config'),
     url(r'^check_project_machineList/', 'hob.projects.views.check_project_machineList'),
     url(r'^delete_project_layer/', 'hob.projects.views.delete_project_layer'),
     url(r'^upload_file/', 'hob.projects.views.upload_file'),
     url(r'^check_layer/', 'hob.projects.views.check_layer'),
)