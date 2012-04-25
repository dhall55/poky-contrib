def include_pkg_child_dep(selected_item, pkg_model, dep_list=[]):
    depends = None
    pkg_list = []
    for item in pkg_model:
        for initem in item['package_value']:
            if initem['size'] == "0" and not initem['allow_empty']:
                continue
            pkg_list.append(initem['pkg'])
            if selected_item == initem['pkg']:
                dep_list.append(selected_item)
                depends = initem['rdep'] + ' ' + initem['rrec']
    if depends:
        for item in depends.split(" "):
            if item.startswith('(') or item.endswith(')') or item =='' or item in dep_list:
                continue
            if item not in pkg_list:
                continue
            dep_list.append(item)
            include_pkg_child_dep(item, pkg_model)
    return list(set(dep_list))

def include_pkg_parent_dep(selected_item, pkg_model, dep_list=[]):
    for item in pkg_model:
        if selected_item == item['package']:
            for initem in item['package_value']:
                dep_list+= include_pkg_child_dep(initem['pkg'],pkg_model)
    return list(set(dep_list))