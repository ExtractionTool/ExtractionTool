

class Flow:
    name = None
    from_process = None
    to_process = None
    enumeration = None
    assets = []
    is_inheritance = False
    appearance_chain = []

    def __init__(self, name, from_process, to_process, enumeration, assets, is_inheritance):
        self.name = name
        self.to_process = to_process
        self.from_process = from_process
        self.enumeration = enumeration
        self.assets = assets
        self.is_inheritance = is_inheritance

    def iterate_assets(self):
        ret_string = ""
        for a in self.assets:
            ret_string += a.name + ", "
        return ret_string
