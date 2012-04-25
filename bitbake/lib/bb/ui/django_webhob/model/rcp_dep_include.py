def rcp_collect_lists(rcp_model, all_rcp_list = [],all_rcpcollect_list = []):
    for item in rcp_model["pn"]:
        if ('task-' not in item and '-image-' not in item and 'meta-' not in item
            and 'lib32-' not in item and 'lib64-' not in item and '-native' not in item):
            all_rcp_list.append(item)
        if ('task-' in item):
            for pkg in rcp_model["pn"][item]["packages"]:
                all_rcp_list.append(pkg)
    return list(set(all_rcp_list))
def map_runtime(event_model, runtime, rdep_type, name):
    if rdep_type not in ['pkg', 'pn'] or runtime not in ['rdepends', 'rrecs']:
        return
    package_depends = event_model["%s-%s" % (runtime, rdep_type)].get(name, [])
    pn_depends = []
    for package_depend in package_depends:
        if 'task-' not in package_depend and package_depend in event_model["packages"].keys():
            pn_depends.append(event_model["packages"][package_depend]["pn"])
        else:
            pn_depends.append(package_depend)
    return list(set(pn_depends))
def include_rcp_dep(selected_item, rcp_model, dep_list=[]):
    if selected_item in rcp_model['pn'].keys():
        depends = rcp_model["depends"].get(selected_item, [])
        depends += map_runtime(rcp_model, 'rdepends', 'pn', selected_item)
        for pkg in rcp_model["pn"][selected_item]["packages"]:
            depends += map_runtime(rcp_model, 'rdepends', 'pkg', selected_item)
            depends += map_runtime(rcp_model, 'rrecs', 'pkg', selected_item)
        if depends:
            for item in depends:
                if '-native' in item or item in dep_list:
                    continue
                dep_list.append(item)
                include_rcp_dep(item, rcp_model)
        dep_list.append(selected_item)
    elif 'task-' in selected_item:
        print selected_item
        dep_list.append(selected_item)
        for i in subpkg_populate(rcp_model, selected_item):
            include_rcp_dep(i, rcp_model)
            dep_list.append(i)
    return list(set(dep_list))
def subpkg_populate(event_model, pkg):
    pn_depends = map_runtime(event_model, "rdepends", "pkg", pkg)
    pn_depends += map_runtime(event_model, "rrecs", "pkg", pkg)
    return pn_depends
def base_image_dep(selected_item, rcp_model, xxxx=[]):
    if '-image-' in selected_item:
        depends = rcp_model["depends"].get(selected_item, [])
        rdepends = map_runtime(rcp_model, 'rdepends', 'pn', selected_item)
        depends = depends + rdepends
        for item in depends:
            if 'task-' in item or 'mltask' in item:
                depends+= subpkg_populate(rcp_model,item)
    return list(set(depends))
def select_base_image_dep(selected_item, rcp_model):
    task_list = []
    rcp_list = []
    deps = base_image_dep(selected_item, rcp_model)
    for item in deps:
       if 'task-' in item:
           task_list.append(item)
       else:
           rcp_list += include_rcp_dep(item, rcp_model)
    return  list(set(task_list+rcp_list))