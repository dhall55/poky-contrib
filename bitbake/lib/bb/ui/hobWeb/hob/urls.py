from django.conf.urls.defaults import patterns, include, url
'''
Created on 2012-4-24

@author: lvchunhx
'''
urlpatterns = patterns('',
    url(r'^index/','hob.views.index'),
    url(r'^login/','hob.views.login'),
    url(r'^edit_user/','hob.views.saveOrupdate_user'),
    url(r'^config_request/','hob.views.config_request'),
    url(r'^get_configEvents/','hob.views.get_configEvents'),
    url(r'^parseRecipe_request/','hob.views.parseRecipe_request'),
    url(r'^parseRecipe_event/','hob.views.parseRecipe_event'),
    url(r'^recipe_task_list/','hob.views.recipe_task_list'),
    url(r'^buildPackage_request/','hob.views.buildPackage_request'),
    url(r'^getPackage_event/','hob.views.getPackage_event'),
    url(r'^package_list/','hob.views.package_list'),
    url(r'^buildImage_request/','hob.views.buildImage_request'),
    url(r'^getImage_event/','hob.views.getImage_event'),
    url(r'^disp_image/','hob.views.disp_image'),
    url(r'^get_recipe_dependency/','hob.views.get_recipe_dependency'),
    url(r'^disp_recipes_tasks/','hob.views.disp_recipes_tasks'),
    url(r'^get_package_dependency/','hob.views.get_package_dependency'),
    url(r'^disp_packages/','hob.views.disp_packages'),
)
