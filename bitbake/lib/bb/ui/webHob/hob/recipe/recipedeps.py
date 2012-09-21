from django.db import connection

class RecipeDeps:
    def __init__(self, recipe_model, guid):
        self.recipe_model = recipe_model
        get_model = self.__get_model()
        self.id_name = get_model[0]
        self.model_dict = get_model[1]
        self.modified_id = []
        self.guid = guid

    def __get_model(self):
        model_dict = {}
        id_name = {}
        tree_model = self.recipe_model
        for i in tree_model:
            id = int(i.id)
            id_name[i.name] = id
            model_dict[id]={
                'name'  : i.name,
                'desc'  : i.desc,
                'lic'   : i.lic,
                'group' : i.group,
                'deps'  : i.deps,
                'binb'  : i.binb,
                'type'  : i.type,
                'is_inc': i.is_inc,
                'is_img': i.is_img,
                'install':i.install,
            }
        return (id_name, model_dict)

    def include_item(self, id, binb="", image_contents=False):
        if self.model_dict[id]['is_inc']==1:
            return

        item_name = self.model_dict[id]['name']
        item_deps = self.model_dict[id]['deps']

        self.model_dict[id]['is_inc'] = 1
        self.modified_id.append(id)

        item_bin = self.model_dict[id]['binb'].split(', ')
        if binb and not binb in item_bin:
            item_bin.append(binb)
            self.model_dict[id]['binb'] = ', '.join(item_bin).lstrip(', ')

        if item_deps:
            # Ensure all of the items deps are included and, where appropriate,
            # add this item to their COL_BINB
            for dep in item_deps.split(" "):
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
                    self.include_item(dep_path, binb=item_name, image_contents=image_contents)

    def find_path_for_item(self, item_name):
        if self.non_target_name(item_name) or item_name not in self.id_name.keys():
            return None
        else:
            return int(self.id_name[item_name])

    def non_target_name(self, name):
        if name and ('-native' in name):
            return True
        return False

    def exclude_item(self, id):
        if not self.model_dict[id]['is_inc']:
            return

        self.model_dict[id]['is_inc'] = 0
        self.modified_id.append(id)

        item_name = self.model_dict[id]['name']
        item_deps = self.model_dict[id]['deps']
        if item_deps:
            for dep in item_deps.split(" "):
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
        try:
            cursor = connection.cursor()
            for i in modified_id:
                sql = '''UPDATE db_recipe_model SET  binb="%s", is_inc=%s, is_img=%s WHERE id = %s and guid = %s''' %\
                     (self.model_dict[i]['binb'],self.model_dict[i]['is_inc'],self.model_dict[i]['is_img'], i, self.guid)
                cursor.execute(sql)
            connection.commit()
            cursor.close()
        except Exception as e:
            print e

    def clear_id(self):
        self.modified_id = []

    def exclude(self, id):
        id=int(id)
        self.clear_id()
        self.exclude_item(id)
        self.update_all_data()

    def include(self, id, binb="", image_contents=False):
        id=int(id)
        self.clear_id()
        self.include_item(id, binb, image_contents)
        self.update_all_data()