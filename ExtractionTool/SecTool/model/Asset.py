

class Asset:
    name = None
    source = None
    targets = []
    values = None
    path = None
    flows = {}
    target_copy_tracker = {}

    def __init__(self, name, source, targets, values):
        self.name = name
        self.source = source
        self.targets = targets
        for t in targets:
            self.target_copy_tracker[t.path_to_file + t.name + t.func_name] = t
        self.values = values

    def append_target(self, new_target):
        comparative_name = new_target.path_to_file + new_target.name + new_target.func_name
        if comparative_name not in self.target_copy_tracker:
            self.targets.append(new_target)
            self.target_copy_tracker[comparative_name] = new_target
