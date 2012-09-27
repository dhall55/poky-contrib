from django.db import models

class RecipeManager(models.Manager):
    def revival_model_tree(self, data):
        for k, v in data.iteritems():
            if not isinstance(v, dict):
                if v.startswith('list:'):
                    v= v.split('list:')[1]
                    data[k] = v.split(', ')
                else:
                    data[k] = v
            if isinstance(v, dict):
                data[k] = self.revival_model_tree(v)
        return data

    def populate(self, event_model, guid):
        event_model = self.revival_model_tree(event_model)

        for item in event_model["pn"]:
            name = item
            desc = event_model["pn"][item]["description"]
            lic = event_model["pn"][item]["license"]
            group = event_model["pn"][item]["section"]
            inherits = event_model["pn"][item]["inherits"]
            install = []

            depends = event_model["depends"].get(item, []) + event_model["rdepends-pn"].get(item, [])
            if ('task-' in name):
                atype = 'task'
            elif ('image.bbclass' in " ".join(inherits)):
                if name != "hob-image":
                    atype = 'image'
                    install = event_model["rdepends-pkg"].get(item, []) + event_model["rrecs-pkg"].get(item, [])
            elif ('meta-' in name):
                atype = 'toolchain'
            elif (name == 'dummy-image' or name == 'dummy-toolchain'):
                atype = 'dummy'
            else:
                atype = 'recipe'

            self.create(guid = guid,
                        name    = item,
                        desc    = desc,
                        lic     = lic,
                        group   = group,
                        deps    = " ".join(depends),
                        binb    = '',
                        type    = atype,
                        is_inc  = 0,
                        is_img  = 0,
                        install = " ".join(install),
            )

class RecipeModel(models.Model):
    guid = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=4000)
    lic = models.CharField(max_length=200)
    group = models.CharField(max_length=1000)
    deps = models.CharField(max_length=5000)
    binb = models.CharField(max_length=5000)
    type = models.CharField(max_length=100)
    is_inc = models.IntegerField()
    is_img = models.IntegerField()
    install = models.CharField(max_length=1000)
    objects = RecipeManager()

    class Meta:
        db_table = u'db_recipe_model'
        ordering = ['name']