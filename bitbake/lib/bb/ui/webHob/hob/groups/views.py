from django.shortcuts import render_to_response
from hob.projects.models import Project, Permissions, RemindMessage
from hob.groups.models import Group
from django.http import HttpResponseRedirect,HttpResponse
from hob.operators.models import Operator
import simplejson
from hob.builds.models import Building

def index(request):
    current_user = request.GET["current_user"].strip()

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)

    temp = []
    for val in Group.objects.all():
        if val.operators.filter(name=current_user):
            temp.append(val.name)
    groups = Group.objects.filter(name__in = temp)
    permissions = Permissions.objects.filter(group__name__in=temp, valid=True)
    return render_to_response("web/groups.html", locals())

'''
add one group, don't allow to add same name group.
'''
def save_group(request):
    current_user = request.POST["current_user"].strip()
    name = request.POST["name"].strip()
    if Group.objects.filter(name=name):
        error = name + " is exist"
        temp = []
        for val in Group.objects.all():
            if val.operators.filter(name=current_user):
                temp.append(val.name)
        groups = Group.objects.filter(name__in = temp)
        permissions = Permissions.objects.filter(group__name__in=temp, valid=True)
        return render_to_response("web/groups.html", locals())
    else:
        group = Group.objects.create(name=name, creator=current_user)
        group.operators.add(Operator.objects.get(name=current_user))
        group.save()
        Permissions.objects.create(group=group)
        Permissions.objects.create(group=group, operators=Operator.objects.get(name=current_user))
        return HttpResponseRedirect("/hob/groups/index/?current_user=%s" % current_user)

'''
add new member to group.
'''
def add_someone_to_group(request):
    sender = request.POST["sender"].strip()
    togroup = request.POST["togroup"].strip()
    receiver = request.POST["receiver_email"].strip()
    remind_content = request.POST["remind_content"].strip()
    #invite remind
    RemindMessage.objects.create(creator=sender, receiver=receiver, types="invite", content=remind_content, valid=True)
    #add new operator to group
    group = Group.objects.get(name=togroup)
    if group.operators.filter(email=receiver):
        pass
    else:
        try:
            operator = Operator.objects.get(email=receiver)
            group.operators.add(operator)
            group.save()
            #assign new operator default permission
            group_permission_default = Permissions.objects.filter(group=group, operators=None, valid=True)[0]
            Permissions.objects.create(group=group, operators=operator, \
                                       ischecked_add_project=group_permission_default.ischecked_add_project, \
                                       ischecked_access_del_builds=group_permission_default.ischecked_access_del_builds, \
                                       ischecked_add_layer=group_permission_default.ischecked_add_layer)
        except Operator.DoesNotExist:
            pass
    return HttpResponseRedirect("/hob/groups/index/?current_user=%s" % sender)

'''
for group member to set permission.
'''
def set_group_permission(request):
    if request.method == "POST":
        current_user = request.POST["creator"].strip()
        group = request.POST["group_permission"].strip()
        user = request.POST["user_permission"].strip()
        permission_list = request.POST.getlist('permission_checkbox')
        ischecked_add_project = False
        ischecked_access_del_builds = False
        ischecked_add_layer = False
        for val in permission_list:
            if val == "edit_project":
                ischecked_add_project = True
            elif val == "edit_builds":
                ischecked_access_del_builds = True
            elif val == "edit_layers":
                ischecked_add_layer = True
        Permissions.objects.filter(group__name=group, operators__name=user).update(ischecked_add_project=ischecked_add_project, \
                                                                                   ischecked_access_del_builds=ischecked_access_del_builds, \
                                                                                   ischecked_add_layer=ischecked_add_layer)
        return HttpResponseRedirect("/hob/groups/index/?current_user=%s" % current_user)

'''
get group member privileges info.
'''
def get_user_permission(request):
    group_name = request.GET["group_name"].strip()
    user_name = request.GET["user_name"].strip()
    edit_project = ""
    edit_builds = ""
    edit_layers = ""
    permission = Permissions.objects.filter(group__name=group_name, operators__name=user_name)[0]
    if permission.ischecked_add_project:
        edit_project="1"
    if permission.ischecked_access_del_builds:
        edit_builds="1"
    if permission.ischecked_add_layer:
        edit_layers="1"
    result_dict = {"edit_project": edit_project, "edit_builds": edit_builds, "edit_layers": edit_layers}
    return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")

def delete_memeber_from_group(request):
    current_user = request.GET["current_user"].strip()
    groupName = request.GET["groupName"].strip()
    operatorSelected = request.GET["operatorSelected"].strip()
    group = Group.objects.get(name=groupName)
    group.operators.remove(Operator.objects.get(name=operatorSelected))
    Permissions.objects.filter(group__name=groupName, operators__name=operatorSelected).delete()
    return HttpResponseRedirect("/hob/groups/index/?current_user=%s" % current_user)

'''
for project group member to set permission.
'''
def set_project_group_permission(request):
    current_user = request.POST["creator"].strip()
    group = request.POST["group_permission"].strip()
    user = request.POST["user_permission"].strip()
    project = request.POST["project_permission"].strip()
    permission_list = request.POST.getlist('permission_checkbox')
    ischecked_add_project = False
    ischecked_access_del_builds = False
    ischecked_add_layer = False
    for val in permission_list:
        if val == "edit_project":
            ischecked_add_project = True
        elif val == "edit_builds":
            ischecked_access_del_builds = True
        elif val == "edit_layers":
            ischecked_add_layer = True
    Permissions.objects.filter(project__name=project, group__name=group, operators__name=user).update(ischecked_add_project=ischecked_add_project, \
                                                                               ischecked_access_del_builds=ischecked_access_del_builds, \
                                                                               ischecked_add_layer=ischecked_add_layer)
    return HttpResponseRedirect("/hob/projects/projects_permisisons/?current_user=%s&current_project=%s" % (current_user, project))

def get_project_user_permission(request):
    group_name = request.GET["group_name"].strip()
    user_name = request.GET["user_name"].strip()
    project_name = request.GET["project_name"].strip()
    edit_project = ""
    edit_builds = ""
    edit_layers = ""
    permission = Permissions.objects.filter(project__name=project_name, group__name=group_name, operators__name=user_name)[0]
    if permission.ischecked_add_project:
        edit_project="1"
    if permission.ischecked_access_del_builds:
        edit_builds="1"
    if permission.ischecked_add_layer:
        edit_layers="1"
    result_dict = {"edit_project": edit_project, "edit_builds": edit_builds, "edit_layers": edit_layers}
    return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")