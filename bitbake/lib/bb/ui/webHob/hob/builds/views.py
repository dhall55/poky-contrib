from django.shortcuts import render_to_response
from hob.builds.models import Building, Builds, Images
from hob.groups.models import Group
from hob.projects.models import Project, Settings, Layers, UserSettings, History,\
    RemindMessage
from django.http import HttpResponseRedirect,HttpResponse
import simplejson,time
from hob.builds.hob_events import HobEvents
from hob.utils.xmlrpc_client import XmlrpcServer
from hob.recipe.models import RecipeModel
from hob.recipe.recipedeps import RecipeDeps
from hob.package.models import PackageModel
from django.db.models import Count,Q
from hob.package.packagedeps import PackageDeps
from hob.operators.models import Operator
from hob.utils.utils import _string_to_size

queue = []
def index(request):
    current_user = request.GET["current_user"].strip()
    #Queue Modal Content
    builds = Builds.objects.filter(operator__name = current_user)
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)
    return render_to_response('web/builds.html',locals())

def index_dashboard(request):
    current_user = request.GET['current_user'].strip()
    builds = Builds.objects.filter(operator__name = current_user)

    groups = Group.objects.filter(creator = current_user)
    projects = Project.objects.filter(creator = current_user)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)
    return render_to_response('web/index_dashboard.html',locals())

'''
send parse recipe command to bitbake by management API interface.
'''
def parseRecipe_request(request):
    current_user = request.POST["current_user"].strip()
    current_project = request.POST["current_project"].strip()
    machine_selected = request.POST["machine_selected"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project ,operator__name=current_user)

    #build config
    config = Settings.objects.get(project__name=current_project)
    layer_list = userSettings.layers_selected.strip().split()
    layers = Layers.objects.filter(project__name=current_project, name__in=layer_list)
    build_config = {}
    build_config["bbthread"]=config.bb_number_threads
    build_config["distro"]=config.distro
    build_config["machine"]=machine_selected
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
            #update userSettings data
            RecipeModel.objects.filter(guid=guid).delete()
            PackageModel.objects.filter(guid=guid).delete()
            userSettings.baseImage_selected=None
            userSettings.recipes_selected=None
            userSettings.packages_selected=None
            userSettings.is_customize_baseImage=False
            userSettings.save()
        else:
            guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
            xmlRpc = XmlrpcServer(guid)
            try:
                if xmlRpc.get_idle_bitbake():
                    #update userSettings data
                    RecipeModel.objects.filter(guid = userSettings.guid).delete()
                    PackageModel.objects.filter(guid = userSettings.guid).delete()
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
                    result_dict = {"result": "error", "msg": "no available bitbake to use!"}
                    return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")
            except Exception:
                result_dict = {"result": "error", "msg": "unable to connect to bitbake!"}
                return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")
    else:
        guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
        xmlRpc = XmlrpcServer(guid)
        try:
            if xmlRpc.get_idle_bitbake():
                userSettings.guid = guid
                userSettings.save()
            else:
                result_dict = {"result": "error", "msg": "no available bitbake to use!"}
                return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")
        except Exception:
            result_dict = {"result": "error", "msg": "unable to connect to bitbake!"}
            return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")

    try:
        if xmlRpc.parse_recipe(build_config):
            userSettings.machine_selected = machine_selected
            userSettings.save()
            Building.objects.filter(project__name=current_project, operator__name=current_user).delete()
            recipe_event_dict = {}
            if queue:
                for val in queue:
                    if val.has_key(guid):
                        queue.remove(val)
            recipe_event_dict[guid]=[]
            queue.append(recipe_event_dict)
            HobEvents(xmlRpc, current_user, current_project, 'recipe', guid, recipe_event_dict[guid]).handle_event()
        else:
            userSettings.valid=False
            userSettings.save()
            result_dict = {"result": "error", "msg": "user's guid is invalid, please try again!"}
            return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")
    except Exception,e:
        result_dict = {"result": "error", "msg": "unable to connect to bitbake!"}
        return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")
    result_dict = {"result":"start to get event"}
    return HttpResponse(content=simplejson.dumps(result_dict), mimetype="text/plain")

'''
get recipe events from bitbake by management API interface.
'''
def recipe_events(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project ,operator__name=current_user)
    events = {}
    if queue:
        for val in queue:
            if val.has_key(userSettings.guid):
                #get recipe queue by guid
                if val[userSettings.guid]:
                    for item in val[userSettings.guid]:
                        for key, value in item.iteritems():
                            if key == "commond_complete":
                                base_images=[ val.name for val in RecipeModel.objects.filter(guid=userSettings.guid, type="image")]
                                events = {"base_images": base_images}
                                return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")
                            else:
                                events[key]=value
                        val[userSettings.guid].remove(item)
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")

'''
get task list
'''
def createbuild_packagegroups(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    buiding = Building.objects.filter(project__name=current_project, operator__name=current_user, is_finished=False)
    userSettings = UserSettings.objects.get(settings__project__name=current_project ,operator__name=current_user)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)

    if userSettings.baseImage_selected == "self-hosted-image":
        RecipeModel.objects.filter(guid=userSettings.guid).update(is_inc=0, binb="")
    tasks = RecipeModel.objects.filter(guid=userSettings.guid, type='task').exclude(name__icontains="native").order_by("name")
    tasks_included = RecipeModel.objects.filter(guid=userSettings.guid, type='task', is_inc=1).exclude(name__icontains="native").order_by("name")
    return render_to_response('web/createbuild_packagegroups.html',locals())

'''
get recipe list
'''
def createbuild_recipes(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project ,operator__name=current_user)
    buiding = Building.objects.filter(project__name=current_project, operator__name=current_user, is_finished=False)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)

    recipes = RecipeModel.objects.filter(guid=userSettings.guid, type='recipe').exclude(name__icontains="native").order_by("name")
    recipes_included = RecipeModel.objects.filter(guid=userSettings.guid, type='recipe', is_inc=1).exclude(name__icontains="native").order_by("name")
    recipes_included_str = ""
    for val in recipes_included:
        recipes_included_str =recipes_included_str+" "+val.name
    return render_to_response('web/createbuild_recipes.html',locals())

'''
by checking recipe item to obtain relevant dependent options.
'''
def search_recipe_dependencies(request):
    current_user = request.GET["current_user"].strip()
    recipe_id = request.GET["recipe_id"].strip()
    is_selected = request.GET["is_selected"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project ,operator__name=current_user)

    #rearch recipe dependency and update recipeModel talbe records
    model = RecipeModel.objects.filter(guid=userSettings.guid)
    deps = RecipeDeps(model, userSettings.guid)
    if is_selected == "1":
        deps.include(recipe_id,binb='User Selected')
    elif is_selected == "0":
        deps.exclude(recipe_id)
    recipeModel = RecipeModel.objects.get(id=recipe_id, guid=userSettings.guid)
    if "task" not in recipeModel.name:
        flag = 0
        historyName = "recipes"
    else:
        flag = 1
        historyName = "package groups"

    #updata UserSettings table records
    recipes_str = ""
    for val in RecipeModel.objects.filter(guid=userSettings.guid, is_inc=1).exclude(type='image'):
        recipes_str = recipes_str + " " + str(val.name)
    UserSettings.objects.filter(settings__project__name=current_project, operator__name=current_user).update(recipes_selected=recipes_str, is_customize_baseImage=True)

    #history
    history_note = "Selected "+recipes_str+" in "+historyName
    History.objects.create(message=history_note, operator=Operator.objects.get(name=current_user), project=Project.objects.get(name=current_project))
    return HttpResponse(content=simplejson.dumps({"result": "ok", "flag": flag}), mimetype="text/plain")

'''
get baseimage dependent options.
'''
def search_baseimage_dependencies(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project ,operator__name=current_user)
    baseimage_selected = request.GET["baseimage_selected"].strip()
    baseimage = RecipeModel.objects.filter(guid=userSettings.guid, type="image", name=baseimage_selected)
    if baseimage:
        if baseimage_selected != "self-hosted-image":
            baseimage_id = baseimage[0].id
            #recipe dependency
            model = RecipeModel.objects.filter(guid=userSettings.guid)
            model.update(is_inc=0,binb='',is_img=0)
            deps = RecipeDeps(model, userSettings.guid)
            deps.include(baseimage_id,binb='User Selected')

            #package dependency
            pkg_model = PackageModel.objects.filter(guid=userSettings.guid)
            if pkg_model:
                pkg_model.update(is_inc=0,binb='')
                recipemodel = RecipeModel.objects.get(id=baseimage_id, guid=userSettings.guid)
                install =  recipemodel.install.split()
                deps = PackageDeps(pkg_model, userSettings.guid)
                for item in install:
                    if item:
                        try:
                            id = PackageModel.objects.get(name=item, guid=userSettings.guid).id
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                        else:
                            deps.include(id,binb='User Selected')

            #updata UserSettings table records
            recipes_str = ""
            for val in RecipeModel.objects.filter(guid=userSettings.guid, is_inc=1).exclude(type='image'):
                recipes_str = recipes_str + " " + str(val.name)
            package_str = ""
            for val in PackageModel.objects.filter(guid=userSettings.guid, is_inc=1):
                package_str = package_str + " " + str(val.name)
            UserSettings.objects.filter(settings__project__name=current_project, operator__name=current_user).update(baseImage_selected=baseimage_selected, recipes_selected=recipes_str, packages_selected=package_str)
        else:
            UserSettings.objects.filter(settings__project__name=current_project, operator__name=current_user).update(baseImage_selected=baseimage_selected, recipes_selected="", packages_selected="")
    else:
        UserSettings.objects.filter(settings__project__name=current_project, operator__name=current_user).update(baseImage_selected="", recipes_selected="", packages_selected="")
    return HttpResponse(content=simplejson.dumps({"result": "ok"}), mimetype="text/plain")

'''
send build package command to bitbake by management API interface.
'''
def createbuild_packages(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)

    #poky not in distro, don't allow user to build package
    if "poky" not in userSettings.settings.distro_list.strip().split():
        request.session[current_user] = "Don't allow to build package without poky in distro list!"
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))

    if Building.objects.filter(guid=userSettings.guid, current_build_task="image", is_finished=True) and Building.objects.filter(guid=userSettings.guid, name=userSettings.baseImage_selected):
        return HttpResponseRedirect("/hob/builds/createbuild_packages_list/?current_user=%s&current_project=%s" % (current_user, current_project))
    elif Building.objects.filter(guid=userSettings.guid, is_finished=False, current_build_task="image"):
        return HttpResponseRedirect("/hob/builds/createbuild_packages_list/?current_user=%s&current_project=%s" % (current_user, current_project))
    elif Building.objects.filter(guid=userSettings.guid, is_finished=True, current_build_task="package") and Building.objects.filter(guid=userSettings.guid, name=userSettings.baseImage_selected):
        return HttpResponseRedirect("/hob/builds/createbuild_packages_list/?current_user=%s&current_project=%s" % (current_user, current_project))
    elif Building.objects.filter(guid=userSettings.guid, is_finished=False, current_build_task="package"):
        building_queue = len(buildings)
        current_building = Building.objects.get(guid=userSettings.guid)
        return render_to_response('web/createbuild_packages.html',locals())
    else:
        #build config
        config = Settings.objects.get(project__name=current_project)
        layer_list = userSettings.layers_selected.strip().split()
        layers = Layers.objects.filter(project__name=current_project, name__in=layer_list)
        build_config = {}
        build_config["bbthread"]=config.bb_number_threads
        build_config["distro"]=config.distro
        build_config["machine"]=userSettings.machine_selected
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
        build_config["selected_recipes"]=userSettings.recipes_selected.strip().split()

        if userSettings.guid:
            if userSettings.valid:
                guid = userSettings.guid
                xmlRpc = XmlrpcServer(guid)
            else:
                guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
                xmlRpc = XmlrpcServer(guid)
                try:
                    if xmlRpc.get_idle_bitbake():
                        guid_old = userSettings.guid
                        PackageModel.objects.filter(guid = userSettings.guid).delete()
                        Building.objects.filter(guid = userSettings.guid).delete()
                        userSettings.guid = guid
                        userSettings.packages_selected=None
                        userSettings.is_customize_baseImage=False
                        userSettings.fast_build_image = None
                        userSettings.valid=True
                        userSettings.save()
                        RecipeModel.objects.filter(guid = guid_old).update(guid=guid)
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
            if xmlRpc.build_package(build_config):
                package_event_dict = {}
                if queue:
                    for val in queue:
                        if val.has_key(userSettings.guid):
                            queue.remove(val)
                package_event_dict[userSettings.guid]=[]
                queue.append(package_event_dict)
                current_building = Building.objects.create(name=userSettings.baseImage_selected, project=Project.objects.get(name=current_project), guid=userSettings.guid, current_build_task="package", operator=Operator.objects.get(name=current_user))
                building_queue = Building.objects.filter(operator__name = current_user, is_finished=False).count()
                HobEvents(xmlRpc, current_user, current_project, 'package', userSettings.guid, package_event_dict[userSettings.guid]).handle_event()
            else:
                userSettings.valid=False
                userSettings.save()
                request.session[current_user] = "user's guid is invalid, please try again!"
                return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
        except Exception,e:
            request.session[current_user] = "build package error!"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
        return render_to_response('web/createbuild_packages.html',locals())

'''
get package events from bitbake by management API interface.
'''
def get_package_events(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    events = {}
    build_queue=[]
    if queue:
        for val in queue:
            if val.has_key(userSettings.guid):
                if val[userSettings.guid]:
                    for item in val[userSettings.guid]:
                        if item.has_key("state"):
                            if item["state"] == "build_configuration":
                                conf_str = ""
                                for value in item["conf"].split("\n"):
                                    if value:
                                        conf_str = conf_str +value+"<br>"
                                userSettings.build_conf = conf_str
                                userSettings.save()

                                val_dict={}
                                val_dict["state"]="build_configuration"
                                val_dict["message"]=userSettings.build_conf
                                build_queue.append(val_dict)
                            elif item["state"] == "buildstarted":
                                userSettings.build_start = item["msg"]
                                userSettings.save()
                                val_dict={}
                                val_dict["state"]="buildstarted"
                                val_dict["message"]=item["msg"]
                                build_queue.append(val_dict)
                                request.session[userSettings.guid+"_start"]=item["msg"]
                            elif item["state"] == "task":
                                val_dict={}
                                val_dict["state"]="task"
                                val_dict["task"]=item["task"]
                                val_dict["package"]=item["package"]
                                val_dict["message"]=item["message"]
                                build_queue.append(val_dict)
                            elif item["state"] == "log_error":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["error"]
                                build_queue.append(val_dict)
                            elif item["state"] == "taskfailed":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["logfile"]
                                build_queue.append(val_dict)
                            elif item["state"] == "command_failed":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["error"]
                                build_queue.append(val_dict)
                            elif item["state"] == "queuetaskfailed":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["taskstring"]
                                build_queue.append(val_dict)
                            elif item["state"] == "buildcompleted":
                                val_dict={}
                                val_dict["state"]="buildcompleted"
                                val_dict["message"]=item["msg"]
                                build_queue.append(val_dict)
                            elif item["state"] == "no_provider":
                                val_dict={}
                                val_dict["state"]="log"
                                val_dict["message"]=item["msg"]
                                build_queue.append(val_dict)
                        if item.has_key("pct"):
                            val_dict={}
                            val_dict["percent"]=item["pct"]
                            build_queue.append(val_dict)
                        if item.has_key("commond_complete"):
                            val_dict={}
                            val_dict["building_result"]=item["commond_complete"]
                            build_queue.append(val_dict)
                        val[userSettings.guid].remove(item)
    if build_queue:
        events["queue"]=build_queue
    else:
        events["queue"]=[]
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")

'''
get package tree list.
'''
def createbuild_packages_list(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    buiding = Building.objects.filter(project__name=current_project, operator__name=current_user, is_finished=False)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)

    #update package's included records
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    if userSettings.packages_selected:
        packages_list = userSettings.packages_selected.strip().split()
        PackageModel.objects.filter(guid=userSettings.guid, name__in=packages_list).update(is_inc=1)
    elif userSettings.baseImage_selected:
        baseimage_id = RecipeModel.objects.get(guid=userSettings.guid, type="image", name=userSettings.baseImage_selected).id
        recipemodel = RecipeModel.objects.get(guid=userSettings.guid, id=baseimage_id)
        install =  recipemodel.install.split()
        deps = PackageDeps(PackageModel.objects.filter(guid=userSettings.guid), userSettings.guid)
        for item in install:
            if item:
                try:
                    id = PackageModel.objects.get(guid=userSettings.guid, name=item).id
                except Exception as e:
                    pass
                else:
                    deps.include(id,binb='User Selected')
        #updata UserSettings table records
        package_str = ""
        for val in PackageModel.objects.filter(guid=userSettings.guid, is_inc=1):
            package_str = package_str + " " + str(val.name)
        UserSettings.objects.filter(settings__project__name=current_project, operator__name=current_user).update(packages_selected=package_str)

    estimated_size = 0.0
    (pkg_list, inc_list, inlcude_count, all_count) = _pkg_data(userSettings.guid)
    included_pkg_str=""
    for val in PackageModel.objects.filter(guid=userSettings.guid, is_inc=1):
        included_pkg_str =included_pkg_str+" "+val.name
        estimated_size += _string_to_size(val.size)
    estimated_size = estimated_size/(1024*1024)
    Building.objects.filter(project__name=current_project, operator__name=current_user).update(estimated_size=estimated_size)
    return render_to_response('web/createbuild_packages_list.html',locals())

'''
by checking package item to obtain relevant dependent options.
'''
def search_package_dependencies(request):
    current_project = request.GET["current_project"].strip()
    current_user = request.GET["current_user"].strip()
    package_id = request.GET["package_id"].strip()
    is_selected = request.GET["is_selected"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)

    #rearch package dependency and update packageModel talbe records
    package_id=package_id.strip(',')
    model = PackageModel.objects.filter(guid=userSettings.guid)
    deps = PackageDeps(model, userSettings.guid)
    if ',' in package_id:
        package_id = package_id.split(',')
        for i in package_id:
            if is_selected == "1":
                deps.include(i,binb='User Selected')
            elif is_selected =="0":
                deps.exclude(i)
    else:
        if is_selected == "1":
            deps.include(package_id,binb='User Selected')
        elif is_selected == "0":
            deps.exclude(package_id)

    #updata UserSettings table records
    package_str = ""
    for val in PackageModel.objects.filter(guid=userSettings.guid, is_inc=1):
        package_str = package_str + " " + str(val.name)
    UserSettings.objects.filter(settings__project__name=current_project, operator__name=current_user).update(packages_selected=package_str, is_customize_baseImage=True)

    #history
    history_note = "Selected "+package_str+" in packages"
    History.objects.create(message=history_note, operator=Operator.objects.get(name=current_user), project=Project.objects.get(name=current_project))
    return HttpResponse(content=simplejson.dumps({"result": "ok"}), mimetype="text/plain")

'''
obtain a single package some detail information.
'''
def get_package_detail(request):
    package_name = request.GET["package_name"].strip()
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    package_info = PackageModel.objects.get(guid=userSettings.guid, name=package_name)
    package_dict = {}
    package_dict["package_name"]=package_info.name
    package_dict["package_summary"]=package_info.summary
    package_dict["package_broughtInBuy"]=package_info.binb
    package_dict["package_section"]=package_info.section
    package_dict["package_size"]=package_info.size
    return HttpResponse(content=simplejson.dumps(package_dict), mimetype="text/plain")

'''
send build image command to bitbake by management API interface.
'''
def createbuild_buildimage(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False)

    if Building.objects.filter(guid=userSettings.guid, is_finished=True, current_build_task="image"):
        return HttpResponseRedirect("/hob/builds/createbuild_buildimage_download/?current_user=%s&current_project=%s" % (current_user, current_project))
    elif Building.objects.filter(guid=userSettings.guid, is_finished=False, current_build_task="image"):
        building_queue = len(buildings)
        current_building = Building.objects.get(guid=userSettings.guid, project__name=current_project, operator__name=current_user)
        return render_to_response('web/createbuild_buildimage.html',locals())
    elif Building.objects.filter(guid=userSettings.guid, is_finished=False, current_build_task="package"):
        building_queue = len(buildings)
        current_building = Building.objects.get(guid=userSettings.guid, project__name=current_project, operator__name=current_user)
        return render_to_response('web/createbuild_packages.html',locals())
    else:
        #build config
        config = Settings.objects.get(project__name=current_project)
        layer_list = userSettings.layers_selected.strip().split()
        layers = Layers.objects.filter(project__name=current_project, name__in=layer_list)
        build_config = {}
        build_config["bbthread"]=config.bb_number_threads
        build_config["distro"]=config.distro
        build_config["machine"]=userSettings.machine_selected
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

        #check whether baseImage libs have changed
        if userSettings.is_customize_baseImage:
            build_config["is_base_image"]=0
            build_config["selected_image"]=userSettings.baseImage_selected+"_"+str(userSettings.guid)
            build_config["toolchain_build"]=config.build_toolchain_value
            build_config["selected_packages"]=userSettings.packages_selected.strip().split()
        else:
            build_config["is_base_image"]=1
            build_config["selected_image"]=userSettings.baseImage_selected
            build_config["toolchain_build"]=[]
            build_config["selected_packages"]=[]

        if userSettings.guid:
            if userSettings.valid:
                guid = userSettings.guid
                xmlRpc = XmlrpcServer(guid)
            else:
                guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
                xmlRpc = XmlrpcServer(guid)
                try:
                    if xmlRpc.get_idle_bitbake():
                        guid_old = userSettings.guid
                        Building.objects.filter(guid = userSettings.guid).delete()
                        userSettings.guid = guid
                        userSettings.is_customize_baseImage=False
                        userSettings.valid=True
                        userSettings.fast_build_image = None
                        userSettings.save()
                        RecipeModel.objects.filter(guid = guid_old).update(guid=guid)
                        PackageModel.objects.filter(guid = guid_old).update(guid=guid)
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
        if xmlRpc.build_image(build_config):
            image_event_dict = {}
            if queue:
                for val in queue:
                    if val.has_key(userSettings.guid):
                        queue.remove(val)
            image_event_dict[userSettings.guid]=[]
            queue.append(image_event_dict)
            Building.objects.filter(guid=userSettings.guid).update(current_build_task="image", build_percent=0, is_finished=False)
            current_building = Building.objects.get(guid=userSettings.guid)
            building_queue = Building.objects.filter(operator__name = current_user, is_finished=False).count()
            HobEvents(xmlRpc, current_user, current_project, 'image', userSettings.guid, image_event_dict[userSettings.guid]).handle_event()
        else:
            userSettings.valid=False
            userSettings.save()
            request.session[current_user] = "user's guid is invalid, please try again!"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    except Exception,e:
        request.session[current_user] = "build image error!"
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    return render_to_response('web/createbuild_buildimage.html',locals())

'''
get image events from bitbake by management API interface.
'''
def get_image_events(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)
    events = {}
    build_queue=[]
    if queue:
        for val in queue:
            if val.has_key(userSettings.guid):
                if val[userSettings.guid]:
                    for item in val[userSettings.guid]:
                        if item.has_key("state"):
                            if item["state"] == "build_configuration":
                                conf_str = ""
                                for value in item["conf"].split("\n"):
                                    if value:
                                        conf_str = conf_str +value+"<br>"
                                userSettings.build_conf = conf_str
                                userSettings.save()

                                val_dict={}
                                val_dict["state"]="build_configuration"
                                val_dict["message"]=conf_str
                                build_queue.append(val_dict)
                            elif item["state"] == "buildstarted":
                                userSettings.build_start = item["msg"]
                                userSettings.save()
                                val_dict={}
                                val_dict["state"]="buildstarted"
                                val_dict["message"]=item["msg"]
                                build_queue.append(val_dict)
                            elif item["state"] == "task":
                                val_dict={}
                                val_dict["state"]="task"
                                val_dict["task"]=item["task"]
                                val_dict["package"]=item["package"]
                                val_dict["message"]=item["message"]
                                build_queue.append(val_dict)
                            elif item["state"] == "log_error":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["error"]
                                build_queue.append(val_dict)
                            elif item["state"] == "taskfailed":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["logfile"]
                                build_queue.append(val_dict)
                            elif item["state"] == "command_failed":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["error"]
                                build_queue.append(val_dict)
                            elif item["state"] == "queuetaskfailed":
                                val_dict={}
                                val_dict["state"]="issue"
                                val_dict["message"]=item["taskstring"]
                                build_queue.append(val_dict)
                            elif item["state"] == "buildcompleted":
                                val_dict={}
                                val_dict["state"]="buildcompleted"
                                val_dict["message"]=item["msg"]
                                build_queue.append(val_dict)
                            elif item["state"] == "no_provider":
                                val_dict={}
                                val_dict["state"]="log"
                                val_dict["message"]=item["msg"]
                                build_queue.append(val_dict)
                        if item.has_key("pct"):
                            val_dict={}
                            val_dict["percent"]=item["pct"]
                            build_queue.append(val_dict)
                        if item.has_key("commond_complete"):
                            val_dict={}
                            val_dict["building_result"]=item["commond_complete"]
                            build_queue.append(val_dict)
                        val[userSettings.guid].remove(item)
    if build_queue:
        events["queue"]=build_queue
    else:
        events["queue"]=[]
    return HttpResponse(content=simplejson.dumps(events), mimetype="text/plain")

'''
get images download list.
'''
def createbuild_buildimage_download(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)

    #Queue Modal Content
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    if buildings:
        is_getPercent = "yes"
    else:
        is_getPercent = ""
    building_queue = len(buildings)
    try:
        build_download = Builds.objects.get(guid=userSettings.guid)
        return render_to_response('web/createbuild_buildimage_download.html',locals())
    except Exception,e:
        Building.objects.filter(guid=userSettings.guid).update(current_build_task="package", build_percent=100, is_finished=True)
        userSettings.fast_build_image = None
        userSettings.save()
        request.session[current_user] = "result:build image failed!"
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))

'''
progress of queue.
'''
def getProgressBar(request):
    current_user = request.GET["current_user"].strip()
    buildings = Building.objects.filter(operator__name=current_user, is_finished=False)
    percent_queue = []
    for val in buildings:
        value_dict = {}
        value_dict["guid"] = val.guid
        value_dict["percent"] = int(val.build_percent)
        value_dict["name"] = val.name
        value_dict["buildTask"] = val.current_build_task
        percent_queue.append(value_dict)
    return HttpResponse(content=simplejson.dumps({"progressPercents": percent_queue}), mimetype="text/plain")

def buildReports(request):
    report_project = request.POST["report_project"].strip()
    report_operator = request.POST["report_operator"].strip()
    message = request.POST["message"].strip()
    error_level = request.POST["error_level"].strip()
    History.objects.create(message=message+"["+error_level+"]", operator=Operator.objects.get(name=report_operator), project=Project.objects.get(name=report_project))
    return HttpResponseRedirect("/hob/builds/index/?current_user=%s" % report_operator)

def shareBuilds(request):
    share_guid = request.POST["share_guid"].strip()
    share_project = request.POST["share_project"].strip()
    share_operator = request.POST["share_operator"].strip()
    receiver = request.POST["share_email"].strip()
    contents = request.POST["contents"].strip()

    Builds.objects.filter(guid=share_guid).update(is_share=True)
    History.objects.create(message=contents, operator=Operator.objects.get(name=share_operator), project=Project.objects.get(name=share_project))
    RemindMessage.objects.create(content=contents, creator=share_operator, receiver=receiver, types="share")
    return HttpResponseRedirect("/hob/builds/index/?current_user=%s" % share_operator)

def delete_builds(request):
    current_user = request.GET["current_user"].strip()
    guid = request.GET["guid"].strip()
    Builds.objects.get(guid=guid).images.all().delete()
    Builds.objects.filter(guid=guid).delete()
    return HttpResponseRedirect("/hob/builds/index/?current_user=%s" % current_user)

def builds_sort(request):
    current_user = request.GET["current_user"].strip()
    sortField = request.GET["sortField"].strip()
    if sortField == "date":
        builds = Builds.objects.filter(operator__name = current_user).order_by("create_date")
    else:
        builds = Builds.objects.filter(operator__name = current_user).order_by("project")
    buildings = Building.objects.filter(operator__name = current_user)
    building_queue = Building.objects.filter(operator__name = current_user, is_finished=False).count()

    if buildings:
        if buildings[0].is_finished:
            current_project = ""
        else:
            current_project = buildings[0].project.name
    return render_to_response('web/builds.html',locals())

'''
fast build image include:
1)build_fast_package :send fast build request to bitbake by management API interface.
2)build_fast_image: redirect to get image events page.
'''
def build_fast_package(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    machine_fastBuild = request.POST["machine_fastBuild"].strip()
    baseImage_fastBuild = request.POST["baseImage_fastBuild"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)

    #poky not in distro, don't allow user to build package
    if "poky" not in userSettings.settings.distro_list.strip().split():
        request.session[current_user] = "Don't allow to build package without poky in distro list!"
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))

    #build config
    config = Settings.objects.get(project__name=current_project)
    layer_list = userSettings.layers_selected.strip().split()
    layers = Layers.objects.filter(project__name=current_project, name__in=layer_list)
    build_config = {}
    build_config["bbthread"]=config.bb_number_threads
    build_config["distro"]=config.distro
    build_config["machine"]=machine_fastBuild
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
    build_config["selected_recipes"]=userSettings.recipes_selected.strip().split()
    build_config["is_fast_mode"]=1
    build_config["selected_image"]=baseImage_fastBuild

    if userSettings.guid:
        if userSettings.valid:
            guid = userSettings.guid
            xmlRpc = XmlrpcServer(guid)
        else:
            guid = time.strftime("%Y%m%d%H%M%S",time.localtime())
            xmlRpc = XmlrpcServer(guid)
            try:
                if xmlRpc.get_idle_bitbake():
                    guid_old = userSettings.guid
                    PackageModel.objects.filter(guid= userSettings.guid).delete()
                    Building.objects.filter(guid=userSettings.guid, project__name=current_project, operator__name=current_user).delete()
                    userSettings.guid = guid
                    userSettings.machine_selected=machine_fastBuild
                    userSettings.baseImage_selected=baseImage_fastBuild
                    userSettings.packages_selected=None
                    userSettings.is_customize_baseImage=False
                    userSettings.valid=True
                    userSettings.save()
                    RecipeModel.objects.filter(guid = guid_old).update(guid=guid)
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
        if xmlRpc.build_image_fast(build_config):
            package_event_dict = {}
            if queue:
                for val in queue:
                    if val.has_key(userSettings.guid):
                        queue.remove(val)
            package_event_dict[userSettings.guid]=[]
            queue.append(package_event_dict)
            current_building = Building.objects.create(name=baseImage_fastBuild, project=Project.objects.get(name=current_project), guid=userSettings.guid, current_build_task="package", operator=Operator.objects.get(name=current_user))
            buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
            building_queue = len(buildings)
            userSettings.fast_build_image = "yes"
            userSettings.save()
            HobEvents(xmlRpc, current_user, current_project, 'package_image', userSettings.guid, package_event_dict[userSettings.guid]).handle_event()
        else:
            userSettings.valid=False
            userSettings.save()
            request.session[current_user] = "user's guid is invalid, please try again!"
            return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    except Exception,e:
        request.session[current_user] = "fast build image error!"
        return HttpResponseRedirect("/hob/projects/projects_myproject/?current_user=%s&current_project=%s" % (current_user,current_project))
    return render_to_response('web/createbuild_packages.html',locals())

def build_fast_image(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)

    #update package's included records
    baseimage_id = RecipeModel.objects.get(guid=userSettings.guid, type="image", name=userSettings.baseImage_selected).id
    recipemodel = RecipeModel.objects.get(guid=userSettings.guid, id=baseimage_id)
    install =  recipemodel.install.split()
    deps = PackageDeps(PackageModel.objects.filter(guid=userSettings.guid), userSettings.guid)
    for item in install:
        if item:
            try:
                id = PackageModel.objects.get(guid=userSettings.guid, name=item).id
            except Exception as e:
                pass
            else:
                deps.include(id,binb='User Selected')
    #updata UserSettings table records
    package_str = ""
    for val in PackageModel.objects.filter(guid=userSettings.guid, is_inc=1):
        package_str = package_str + " " + str(val.name)
    userSettings.packages_selected = package_str
    userSettings.save()

    estimated_size = 0.0
    for val in PackageModel.objects.filter(guid=userSettings.guid, is_inc=1):
        estimated_size += _string_to_size(val.size)
    estimated_size = estimated_size/(1024*1024)
    Building.objects.filter(project__name=current_project, operator__name=current_user).update(estimated_size=estimated_size)

    current_building = Building.objects.get(guid=userSettings.guid)
    buildings = Building.objects.filter(operator__name = current_user, is_finished=False, valid=True)
    building_queue = len(buildings)
    return render_to_response('web/createbuild_buildimage.html',locals())

'''
stop building package or image.
'''
def stop_building(request):
    current_user = request.GET["current_user"].strip()
    current_project = request.GET["current_project"].strip()
    current_task = request.GET["current_task"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user, valid=True)
    value_dict = {}

    xmlRpc = XmlrpcServer(userSettings.guid)
    try:
        xmlRpc.stop_build("true")
        if current_task == "package":
            Building.objects.filter(guid=userSettings.guid).delete()
        else:
            Building.objects.filter(guid=userSettings.guid).update(current_build_task="package", build_percent=100, is_finished=True)
        userSettings.fast_build_image = None
        userSettings.save()
        value_dict["result"]="ok"
    except Exception:
        pass
    return HttpResponse(content=simplejson.dumps(value_dict), mimetype="text/plain")

'''
in builds page to stop building package or image.
'''
def cancel_buildings(request):
    current_project = request.POST["current_project"].strip()
    current_user = request.POST["current_user"].strip()
    current_task = request.POST["current_task"].strip()
    userSettings = UserSettings.objects.get(settings__project__name=current_project, operator__name=current_user)

    xmlRpc = XmlrpcServer(userSettings.guid)
    try:
        xmlRpc.stop_build("true")
        if current_task == "package":
            Building.objects.filter(guid=userSettings.guid).delete()
        else:
            Building.objects.filter(guid=userSettings.guid).update(current_build_task="package", build_percent=100, is_finished=True)
        userSettings.fast_build_image = None
        userSettings.save()
    except Exception:
        pass
    return HttpResponseRedirect("/hob/builds/index/?current_user=%s" % current_user)

def _pkg_data(guid):
    #all pkgs
    pkg_list = []
    inc_list = []
    group = PackageModel.objects.filter(guid=guid).values('pnpvpr').annotate(count=Count('pnpvpr'))
    for i_out in group:
        alldata = []
        allpkgs = PackageModel.objects.filter(guid=guid, pnpvpr=i_out['pnpvpr'])
        group={
              'count' : i_out['count'],
              'group_name' : i_out['pnpvpr'],
              'group_inc_id' : ','.join([str(i.id) for i in allpkgs if i.is_inc ]),
        }
        for i in allpkgs:
            data_item = {
                'id'         : i.id,
                'name'         : i.name,
                'summary'      : i.summary,
                'size'         : i.size,
                'binb'         : i.binb,
                'is_inc'       : i.is_inc,
              }
            alldata.append(data_item)
        pkg_list.append((group, alldata))

        #incliude pkgs
    group = PackageModel.objects.filter(guid=guid, is_inc=1).values('pnpvpr').annotate(count=Count('pnpvpr'))
    for i_out in group:
        incluedata = []
        allpkgs = PackageModel.objects.filter(guid=guid, pnpvpr=i_out['pnpvpr'],is_inc=1)
        group={
              'count' : i_out['count'],
              'group_name' : i_out['pnpvpr'],
              'group_inc_id' : ','.join([str(i.id) for i in allpkgs if i.is_inc ]),
        }

        for i in allpkgs:
            data_item = {
                'id'         : i.id,
                'name'         : i.name,
#                'pkgv'         : i.pkgv,
#                'pkgr'         : i.pkgr,
#                'pkg_rename'   : i.pkg_rename,
                'summary'      : i.summary,
#                'rdep'         : i.rdep,
#                'rprov'        : i.rprov,
                'size'         : i.size,
                'binb'         : i.binb,
                'is_inc'       : i.is_inc,
              }
            incluedata.append(data_item)
        inc_list.append((group, incluedata))

    inlcude_count = len(PackageModel.objects.filter(guid=guid, is_inc=1))
    all_count  = len(PackageModel.objects.filter(guid=guid))
    return pkg_list, inc_list, inlcude_count, all_count
