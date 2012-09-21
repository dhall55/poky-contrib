from django.db import connection
class PackageDeps:
    def __init__(self, package_model, guid):
        self.package_model = package_model
        get_model = self.__get_model()
        self.id_name = get_model[0]
        self.rprov_pkg = get_model[1]
        self.model_dict = get_model[2]
        self.modified_id = []
        self.guid = guid

    def __get_model(self):
        model_dict = {}
        id_name = {}
        rprov_pkg = {}
        tree_model = self.package_model
        for i in tree_model:
            id = int(i.id)
            id_name[i.name] = id

            for rpv in i.rprov.split():
                rprov_pkg[rpv] = i.name

            model_dict[id]={
                'name'         : i.name,
                'pkgv'         : i.pkgv,
                'pkgr'         : i.pkgr,
                'pkg_rename'   : i.pkg_rename,
                'summary'      : i.summary,
                'rdep'         : i.rdep,
                'rprov'        : i.rprov,
                'size'         : i.size,
                'binb'         : i.binb,
                'is_inc'       : i.is_inc,
            }
        return (id_name,rprov_pkg, model_dict)

    def find_path_for_item(self, name):
        pkg = name
        if name not in self.id_name.keys():
            if name not in self.rprov_pkg.keys():
                return None
            pkg = self.rprov_pkg[name]
            if pkg not in self.id_name.keys():
                return None
        return int(self.id_name[pkg])

    def include_item(self, id, binb=""):
        if self.model_dict[id]['is_inc']==1:
            return

        item_name = self.model_dict[id]['name']
        item_rdep = self.model_dict[id]['rdep']
        self.model_dict[id]['is_inc'] = 1
        self.modified_id.append(id)

        item_bin = self.model_dict[id]['binb'].split(', ')
        if binb and not binb in item_bin:
            item_bin.append(binb)
            self.model_dict[id]['binb'] = ', '.join(item_bin).lstrip(', ')

        if item_rdep:
            item_rdep = item_rdep
            # Ensure all of the items deps are included and, where appropriate,
            # add this item to their COL_BINB
            for dep in item_rdep.split(" "):
                if dep.startswith('('):
                    continue
                # If the contents model doesn't already contain dep, add it
                dep_path = self.find_path_for_item(dep)
                if not dep_path:
                    continue
                dep_included = self.model_dict[dep_path]['is_inc']

                if dep_included and not dep in item_bin:
                    # don't set the COL_BINB to this item if the target is an
                    # item in our own COL_BINB
                    dep_bin = self.model_dict[dep_path]['binb'].split(', ')
                    if not item_name in dep_bin:
                        dep_bin.append(item_name)
                        self.model_dict[dep_path]['binb'] = ', '.join(dep_bin).lstrip(', ')
                elif not dep_included:
                    self.include_item(dep_path, binb=item_name)

    def exclude_item(self, id):
        if self.model_dict[id]['is_inc']==0:
            return

        self.model_dict[id]['is_inc'] = 0
        self.modified_id.append(id)

        item_name = self.model_dict[id]['name']
        item_rdep = self.model_dict[id]['rdep']

        # All packages that depends on this package are de-selected.
        if item_rdep:
            for dep in item_rdep.split(" "):
                if dep.startswith('('):
                    continue
                dep_path = self.find_path_for_item(dep)
                if not dep_path:
                    continue
                dep_bin = self.model_dict[dep_path]['binb'].split(', ')
                if item_name in dep_bin:
                    dep_bin.remove(item_name)
                    self.model_dict[dep_path]['binb'] = ', '.join(dep_bin).lstrip(', ')

        item_bin = self.model_dict[id]['binb'].split(', ')
        if item_bin:
            for binb in item_bin:
                binb_path = self.find_path_for_item(binb)
                if not binb_path:
                    continue
                self.exclude_item(binb_path)

    def update_all_data(self):
        modified_id = list(set(self.modified_id))
        cursor = connection.cursor()
        for i in modified_id:
            sql = '''UPDATE db_package_model SET  binb="%s", is_inc=%s WHERE id = %s and guid = %s''' %\
                 (self.model_dict[i]['binb'],self.model_dict[i]['is_inc'], i, self.guid)
            cursor.execute(sql)
        cursor.close()

    def clear_id(self):
        self.modified_id = []

    def exclude(self, id):
        id=int(id)
        self.clear_id()
        self.exclude_item(id)
        self.update_all_data()

    def include(self, id, binb=""):
        id=int(id)
        self.clear_id()
        self.include_item(id, binb)
        self.update_all_data()