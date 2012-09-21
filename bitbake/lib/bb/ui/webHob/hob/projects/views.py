from django.shortcuts import render_to_response
from hob.projects.models import Project, RemindMessage, Permissions, History,\
    Layers, Settings, UserSettings
from hob.groups.models import Group
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.http import HttpResponseRedirect,HttpResponse
import simplejson,time,os
from hob.operators.models import Operator
from hob.utils.xmlrpc_client import XmlrpcServer
from hob.builds.hob_events import HobEvents
from hob.recipe.models import RecipeModel
from hob.builds.models import Builds, Building
from hob.package.models import PackageModel
from hob.projects.ftpclient import UploadLayers
from settings import FILE_SERV_INTERFACE, UPLOAD_FILE_SERV_UID,\
    UPLOAD_FILE_SERV_PW, LAYER_UPLOAD_DIR

def index(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)

    temp = []
    for val in Project.objects.all():
        if val.operators.filter(name=current_user):
            temp.append(val.name)
    projects = Project.objects.filter(name__in = temp)
    return render_to_response("web/projects.html", locals())

def save_project(request):
    current_user = request.POST["current_user"].strip()
    project_name = request.POST["name"].strip()
    if Project.objects.filter(name=project_name):
        error ="*" + project_name + " is exist"
        projects = Project.objects.filter(creator = current_user)
        return render_to_response("web/projects.html", locals())
    else:
        #start to get settings config
        guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
        xmlRpc = XmlrpcServer(guid)
        try:
            if xmlRpc.get_idle_bitbake():
                try:
                    if xmlRpc.get_initialize_settings_config():
                        #create project
                        project = Project.objects.create(name = project_name, creator = current_user)
                        project.operators.add(Operator.objects.get(name=current_user))
                        project.save()
                        HobEvents(xmlRpc, current_user, project_name, 'settings', guid).handle_event()
                        return HttpResponseRedirect("/hob/projects/index/?current_user=%s&current_project=%s" % (current_user, project_name))
                    else:
                        error = "get advance settings config error!"
                        projects = Project.objects.filter(creator = current_user)
                        return render_to_response("web/projects.html", locals())
                except Exception:
                    error = "get advance settings config error!"
                    projects = Project.objects.filter(creator = current_user)
                    return render_to_response("web/projects.html", locals())
            else:
                error = "no available bitbake to use!"
                projects = Project.objects.filter(creator = current_user)
                return render_to_response("web/projects.html", locals())
        except Exception,e:
            error = "*" + "bitbake server is not connected!"
            projects = Project.objects.filter(creator = current_user)
            return render_to_response("web/projects.html", locals())

def projects_myproject(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    my_groups = Group.objects.filter(creator=current_user)
    project = Project.objects.get(name=current_project)

    #get asynconfig
    if Settings.objects.get(project__name=current_project).machine_list:
        machines_list = Settings.objects.get(project__name=current_project).machine_list.strip().split()
    else:
        machines_list = []

    if machines_list:
        machines = "yes"
    else:
        machines = ""

    layer_str =""
    for val in Layers.objects.filter(project__name=current_project, ischecked=True).order_by("name"):
        layer_str = layer_str + " "+val.name
    #user's setting
    if UserSettings.objects.filter(operator__name=current_user, settings__project__name=current_project):
        userSettings = UserSettings.objects.get(operator__name=current_user, settings__project__name=current_project)
        if userSettings.valid:
            userSettings.layers_selected = layer_str
            userSettings.save()
    else:
        userSettings = UserSettings.objects.create(settings=Settings.objects.get(project__name=current_project), operator=Operator.objects.get(name=current_user), layers_selected=layer_str)

    baseimage_str =""
    for val in RecipeModel.objects.filter(guid=userSettings.guid, type="image"):
        baseimage_str=baseimage_str+" "+str(val.name)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)

    #builds
    builds = Builds.objects.filter(project__name=current_project, valid=True)
    #error_message
    if request.session.get(current_user):
        error_message = request.session.get(current_user)
        del request.session[current_user]
    else:
        error_message = ""
    if Building.objects.filter(project__name=current_project, operator__name=current_user, is_finished=False):
        is_modify_machine_baseImage = "no"
    else:
        is_modify_machine_baseImage = ""

    #project members and groups
    project_members_list = [val.name for val in project.operators.all()]
    project_group_members_list = []
    for val in project.groups.all():
        for item in val.operators.all():
            if item.name not in project_group_members_list:
                project_group_members_list.append(item.name)
    for val in project_group_members_list:
        if val in project_members_list:
            project_members_list.remove(val)

    #layers
    after_range_num=5
    bevor_range_num=4
    try:
        page=int(request.GET.get("page",1))
        if page<1:
            page = 1
    except ValueError:
        page = 1
    info = Layers.objects.filter(project__name=current_project).order_by("name")
    paginator=Paginator(info,8)
    try:
        layerList = paginator.page(page)
    except(EmptyPage,InvalidPage,PageNotAnInteger):
        layerList = paginator.page(1)
    if page>=after_range_num:
        page_range=paginator.page_range[page-after_range_num:page+bevor_range_num]
    else:
        page_range=paginator.page_range[0:int(page)+bevor_range_num]
    return render_to_response("web/projects_myproject.html", locals())

def add_someone_to_project(request):
    sender = request.POST["sender"].strip()
    current_project = request.POST["current_project"].strip()
    receiver = request.POST["receiver_email"].strip()
    invite_content = request.POST["invite_content"].strip()
    #invite remind
    RemindMessage.objects.create(creator=sender, receiver=receiver, types="invite", content=invite_content, valid=True)
    project = Project.objects.get(name=current_project)
    if project.operators.filter(email=receiver):
        pass
    else:
        project.operators.add(Operator.objects.get(email=receiver))
        project.save()
        history_note = "Invite "+receiver+" to "+current_project+"!"
        History.objects.create(message=history_note, operator=Operator.objects.get(name=sender), project=project)
    return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (sender,current_project))

def add_mygroup_to_project(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    group_selected = request.GET["group_selected"].strip()
    #get group/project queryset
    group = Group.objects.get(name=group_selected, valid=True)
    project = Project.objects.get(name=current_project)
    group_member_list = []
    flag = "0"
    message=""

    if project.groups.filter(name=group.name):
        message=group.name+" has been added!"
        pass
    else:
        flag = "1"
        #add group to project
        project.groups.add(group)
        project.save()

        #add group members to project
        for val in group.operators.all():
            if val.name not in group_member_list:
                group_member_list.append(val.name)
            if project.operators.filter(name=val.name):
                continue
            else:
                project.operators.add(Operator.objects.get(name=val.name))
                project.save()

        #update group operate permissions
        permission_group = Permissions.objects.filter(group__name=group_selected, project=None)
        if permission_group:
            Permissions.objects.filter(group__name=group_selected, project=None).update(project=project)
        else:
            if Permissions.objects.filter(group__name=group_selected, project=project):
                pass
            else:
                Permissions.objects.create(project=project, group=group)
                for val in group_member_list:
                    Permissions.objects.create(project=project, group=group, operators=Operator.objects.get(name=val))
        message=group.name+" added successfully!"
        history_note = "Add "+group_selected+" to "+current_project+"!"
        History.objects.create(message=history_note, operator=Operator.objects.get(name=current_user), project=project)
    result_dict = {"result": message, "flag":flag, "current_user": current_user, "current_project": current_project}
    return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")

def projects_history(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    history = History.objects.filter(project__name=current_project)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)
    return render_to_response("web/projects_history.html", locals())

def projects_settings(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)

    #get setting config
    advance_setting = Settings.objects.get(project__name=current_project)
    image_types = advance_setting.image_type_list.strip().split()
    package_format = advance_setting.package_format_list.strip().split()
    build_toolchain = advance_setting.build_toolchain_list.strip().split()
    distro = advance_setting.distro_list.strip().split()
    image_type_selected = advance_setting.image_types.strip().split()
    pkg_format_selected = advance_setting.package_formats.strip().split()
    image_rooft_size = advance_setting.image_rootfs_size/1024
    pkgs=[]
    if len(pkg_format_selected)>1:
        for val in pkg_format_selected:
            if val not in pkgs:
                pkgs.append(val)
        pkg_format_selected = pkgs.pop()
    else:
        pkg_format_selected = pkg_format_selected[0]
    return render_to_response("web/projects_settings.html", locals())

def save_advance_settings(request):
    current_user = request.POST["current_user"].strip()
    current_project = request.POST["current_project"].strip()
    image_types = request.POST.getlist('checkbox')
    package_format = request.POST["package_formats"]
    pkg_checkbox = request.POST.getlist('pkg_checkbox')
    image_rooft_size = int(request.POST["image_rooft_size"])*1024
    image_extra_size = request.POST["image_extra_size"]
    gplv3_checkbox = request.POST.getlist('gplv3_checkbox')
    build_toolchain_checkbox = request.POST.getlist('build_toolchain_checkbox')
    build_toolchain = request.POST["build_toolchain"]
    distro = request.POST["distro"]
    images_str = ""
    if image_types:
        for val in image_types:
            images_str=images_str+" "+val
    pkg_str = ""
    if pkg_checkbox:
        for val in pkg_checkbox:
            pkg_str=pkg_str+" "+val
    pkg_str = pkg_str+" "+package_format
    gplv3_str =""
    if gplv3_checkbox:
        gplv3_str = gplv3_checkbox[0]
    toolchain_boolean = False
    if build_toolchain_checkbox:
        toolchain_boolean=True
    Settings.objects.filter(project__name=current_project).update(image_types=images_str.strip(), \
                                                                package_formats=pkg_str.strip(), \
                                                                image_rootfs_size=str(image_rooft_size), \
                                                                image_extra_size=image_extra_size, \
                                                                gplv3_checkbox=gplv3_str, \
                                                                build_toolchain_checkbox=toolchain_boolean, \
                                                                build_toolchain_value=build_toolchain, \
                                                                distro=distro)
    history_note = "Changed setting on the "+current_project
    History.objects.create(message=history_note, operator=Operator.objects.get(name=current_user), project=Project.objects.get(name=current_project))
    return HttpResponseRedirect("/hob/projects/projects_settings/?current_user=%s&current_project=%s" % (current_user,current_project))

def check_project_config(request):
    current_project = request.GET["current_project"].strip()
    project_settings = Settings.objects.filter(project__name=current_project)
    value_dict ={}
    if project_settings:
        value_dict["result"]="yes"
    else:
        value_dict["result"]="no"
    return HttpResponse(content=simplejson.dumps(value_dict), mimetype="text/plain")

def check_project_machineList(request):
    current_project = request.GET["current_project"].strip()
    project_settings = Settings.objects.get(project__name=current_project)
    value_dict ={}
    if project_settings.machine_list:
        value_dict["result"]="yes"
        value_dict["error_msg"]=project_settings.note
    else:
        value_dict["result"]="no"
    return HttpResponse(content=simplejson.dumps(value_dict), mimetype="text/plain")

def delete_project_layer(request):
    layerName = request.GET["layerName"].strip()
    current_project = request.GET["current_project"].strip()
    current_user = request.GET["current_user"].strip()

    #config params
    config = Settings.objects.get(project__name=current_project)
    layers = Layers.objects.filter(project__name=current_project).exclude(name=layerName)
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    if userSettings.machine_selected:
        machine = userSettings.machine_selected
    else:
        machine = "qemux86"

    build_config = {}
    build_config["bbthread"]=config.bb_number_threads
    build_config["distro"]=config.distro
    build_config["machine"]=machine
    build_config["package_format"]=config.package_formats
    build_config["sdk_machine"]=config.build_toolchain_value
    build_config["sstatedir"]=config.sstate_directory
    build_config["sstatemirror"]=config.sstate_mirror
    build_config["dldir"]=config.download_directory
    build_config["extra_setting"] ={}
    build_config["image_extra_size"]=config.image_extra_size
    build_config["image_rootfs_size"]=config.image_rootfs_size
    build_config["incompat_license"]=config.gplv3_checkbox
    build_config["layers"]=[val.url for val in layers]
    build_config["pmake"]=config.parellel_make

    if userSettings.guid:
        if userSettings.valid:
            guid = userSettings.guid
            xmlRpc = XmlrpcServer(guid)
        else:
            guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
            xmlRpc = XmlrpcServer(guid)
            try:
                if xmlRpc.get_idle_bitbake():
                    RecipeModel.objects.filter(guid= userSettings.guid).delete()
                    PackageModel.objects.filter(guid= userSettings.guid).delete()
                    Building.objects.filter(guid = userSettings.guid).delete()
                    userSettings.guid = guid
                    userSettings.machine_selected=None
                    userSettings.baseImage_selected=None
                    userSettings.recipes_selected=None
                    userSettings.packages_selected=None
                    userSettings.is_customize_baseImage=False
                    userSettings.valid=True
                    userSettings.save()
                else:
                    request.session[current_user] = "no available bitbake to use!"
                    return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
            except Exception:
                request.session[current_user] = "unable to connect to bitbake!"
                return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    else:
        guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
        xmlRpc = XmlrpcServer(guid)
        try:
            if xmlRpc.get_idle_bitbake():
                userSettings.guid = guid
                userSettings.save()
            else:
                request.session[current_user] = "no available bitbake to use!"
                return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
        except Exception:
            request.session[current_user] = "unable to connect to bitbake!"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    try:
        if xmlRpc.update_settings_config(build_config):
            #reload advanceSettings config flag
            config.machine_list=""
            config.save()
            Layers.objects.filter(project__name=current_project, name=layerName).delete()
            HobEvents(xmlRpc, current_user, current_project, 'settings', guid).handle_event()
        else:
            userSettings.valid=False
            userSettings.save()
            request.session[current_user] = "user's guid is invalid, please try again!"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    except Exception,e:
        request.session[current_user] = "unable to connect to bitbake!"
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user, current_project))

def upload_file(request):
    current_project = request.POST["current_project"].strip()
    current_user = request.POST["current_user"].strip()

    try:
        layer_file = request.FILES.get('filename','')
        uploader = UploadLayers(interface=FILE_SERV_INTERFACE, uid=UPLOAD_FILE_SERV_UID, password=UPLOAD_FILE_SERV_PW, layer_root_dir=LAYER_UPLOAD_DIR)
        result, new_layer_path = uploader.transmit(current_project, layer_file)
        if 'transmition completed' not in result:
            request.session[current_user] = "transmit not complete"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user, current_project))
    except Exception, e:
        request.session[current_user] = e
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user, current_project))

    #reload advance setting
    config = Settings.objects.get(project__name=current_project)
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    layer_list = userSettings.layers_selected.strip().split()
    layers = Layers.objects.filter(project__name=current_project, name__in=layer_list)
    if userSettings.machine_selected:
        machine = userSettings.machine_selected
    else:
        machine = "qemux86"
    build_config = {}
    build_config["bbthread"]=config.bb_number_threads
    build_config["distro"]=config.distro
    build_config["machine"]=machine
    build_config["package_format"]=config.package_formats
    build_config["sdk_machine"]=config.build_toolchain_value
    build_config["sstatedir"]=config.sstate_directory
    build_config["sstatemirror"]=config.sstate_mirror
    build_config["dldir"]=config.download_directory
    build_config["extra_setting"] ={}
    build_config["image_extra_size"]=config.image_extra_size
    build_config["image_rootfs_size"]=config.image_rootfs_size
    build_config["incompat_license"]=config.gplv3_checkbox
    build_config["layers"]=[val.url for val in layers] + [new_layer_path]
    build_config["pmake"]=config.parellel_make

    if userSettings.guid:
        if userSettings.valid:
            guid = userSettings.guid
            xmlRpc = XmlrpcServer(guid)
        else:
            guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
            xmlRpc = XmlrpcServer(guid)
            try:
                if xmlRpc.get_idle_bitbake():
                    RecipeModel.objects.filter(guid= userSettings.guid).delete()
                    PackageModel.objects.filter(guid= userSettings.guid).delete()
                    Building.objects.filter(guid = userSettings.guid).delete()
                    userSettings.guid = guid
                    userSettings.machine_selected=None
                    userSettings.baseImage_selected=None
                    userSettings.recipes_selected=None
                    userSettings.packages_selected=None
                    userSettings.is_customize_baseImage=False
                    userSettings.valid=True
                    userSettings.save()
                else:
                    request.session[current_user] = "no available bitbake to use!"
                    return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
            except Exception:
                request.session[current_user] = "unable to connect to bitbake!"
                return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    else:
        guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
        xmlRpc = XmlrpcServer(guid)
        try:
            if xmlRpc.get_idle_bitbake():
                userSettings.guid = guid
                userSettings.save()
            else:
                request.session[current_user] = "no available bitbake to use!"
                return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
        except Exception:
            request.session[current_user] = "unable to connect to bitbake!"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    try:
        if xmlRpc.update_settings_config(build_config):
            #reload advanceSettings config flag
            config.note = config.machine_list
            config.machine_list=""
            config.save()
            HobEvents(xmlRpc, current_user, current_project, 'settings', guid).handle_event()
        else:
            userSettings.valid=False
            userSettings.save()
            request.session[current_user] = "user's guid is invalid, please try again!"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    except Exception,e:
        request.session[current_user] = "unable to connect to bitbake!"
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user, current_project))

def projects_permisisons(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    project = Project.objects.get(name=current_project)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)
    return render_to_response("web/projects_permissions.html", locals())

def check_layer(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    is_selected = request.GET["is_selected"].strip()
    layer_selected = request.GET["layer_selected"].strip()

    if is_selected == "0":
        Layers.objects.filter(project__name=current_project, name=layer_selected).update(ischecked=False)
    else:
        Layers.objects.filter(project__name=current_project, name=layer_selected).update(ischecked=True)
    return HttpResponse(content=simplejson.dumps({}), mimetype="text/plain")