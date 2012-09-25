try:
    import json
except ImportError:
    import simplejson as json

def covent_json(var):
    if isinstance(var, str):
        return var
    else:
        return json.dumps(var)

def dict_hook(dict_var):
    '''
    convert json object to python object.
    '''
    if isinstance(dict_var, dict):
        o = JsonObject()
        for k, v in dict_var.iteritems():
            o[str(k)] = v
        return o
    else:
        return dict_var

class JsonObject(dict):
    '''
    general json object that can bind any fields but also act as a dict.
    '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

#----------only test-------generate_guid()---------------------------------
def generate_guid():
    import random, hashlib
    str = ''
    for i in range(10):
        str+= chr(random.randint(97, 122))
    return hashlib.new("md5", str).hexdigest()



def ppp(var):
    import pprint
    if isinstance(var, str):
        try:
            pprint.pprint(json.loads(var))
        except:
            print var
    else:
        pprint.pprint(var)

if __name__ == '__main__':
    test_dict = {'k1':{'v1':'vv1'},
                 'k2':'v2',
                 'k3':'v3',
                 'k4':'v4',
                 'k5':'v5',
    }
    new_var = dict_hook(test_dict)
    print new_var.k1.v1