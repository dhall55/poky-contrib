'''
Created on 2012-5-25
@author: lvchunhX
'''
import settings,simplejson
from django.shortcuts import render_to_response
from hob.models import TreeModel, BuildConfig
from utils import rcp_dep_include
from django.http import HttpResponseRedirect,HttpResponse
tree_model = None
def recipe_task_list(request):
    current_user = request.session.get("username")
    recipes = TreeModel.objects.filter(types='recipe').filter(operator__username=current_user).order_by("name")
    tasks = TreeModel.objects.filter(types='task').filter(operator__username=current_user).order_by("name")
    recipes_count = TreeModel.objects.filter(types__in=['recipe', 'task'], operator__username=current_user).count()
    included = TreeModel.objects.filter(is_included=True).filter(operator__username=current_user)
    return render_to_response('web/recipe_task_list.html',locals())

def get_recipe_dependency(request):
    selected_recipe = request.GET.get("selected_recipe").encode().strip()
    is_checked = request.GET.get("is_checked").encode().strip()
    tree_file = open (settings.TEMPLATE_PATH+"/recipeTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()
    tree_dict = eval(tree_str)
    tree_model = tree_dict['model']

    recipeDependency_list = []
    if 'task-' not in selected_recipe:
        recipeDependency_list = rcp_dep_include.include_rcp_dep(selected_recipe,tree_model)
    else:
        recipeDependency_list.append(selected_recipe)

    if is_checked =='0':
        TreeModel.objects.filter(name__in=recipeDependency_list).update(is_included=False)
    else:
        TreeModel.objects.filter(name__in=recipeDependency_list).update(is_included=True)
    return HttpResponseRedirect('/hob/recipe_task_list/')

def get_baseImage_dependency(request):
    baseImage = request.GET.get("baseImage").encode().strip()
    current_user = request.session.get("username")
    tree_file = open (settings.TEMPLATE_PATH+"/recipeTreeModel.txt")
    tree_str = tree_file.read()
    tree_file.close()
    tree_dict = eval(tree_str)
    tree_model = tree_dict['model']
    BuildConfig.objects.filter(operator__username=current_user, build_result=False).update(base_image=baseImage)

    values_list = rcp_dep_include.select_base_image_dep(baseImage,tree_model)
    for item in values_list:
        TreeModel.objects.filter(name=str(item)).update(is_included=True)
    return HttpResponse(content=simplejson.dumps({'baseImage':baseImage}), mimetype="text/plain")