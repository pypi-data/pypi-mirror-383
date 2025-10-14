from geezlibs.geez.database import db_x

db = db_x
collection = db['globals']

class Globals:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def to_dict(self):
        return {'variable': self.variable, 'value': self.value}

    @staticmethod
    def from_dict(data):
        return Globals(data['variable'], data['value'])


def gvarstatus(variable):
    try:
        result = collection.find_one({'variable': variable})
        if result:
            return result['value']
        else:
            return None
    except BaseException:
        return None


def addgvar(variable, value):
    if collection.find_one({'variable': variable}):
        delgvar(variable)
    data = Globals(variable, value).to_dict()
    collection.insert_one(data)


def delgvar(variable):
    result = collection.delete_one({'variable': variable})
    if result.deleted_count > 0:
        return True
    else:
        return False