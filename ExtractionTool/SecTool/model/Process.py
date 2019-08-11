from SecTool.model import Flow

class Process:
    name = None
    enumeration = None
    outgoing_flows = []
    incoming_flows = []
    responsibilities = []
    assets = []
    path_to_file = None
    func_name = None
    asset_copy_tracker = {}

    def __init__(self, name, enumeration, outgoing_flows, incoming_flows, assets, path_to_file):
        self.name = name
        self.enumeration = enumeration
        self.outgoing_flows = outgoing_flows
        self.incoming_flows = incoming_flows
        for a in assets:
            self.append_asset(a)
        self.path_to_file = path_to_file

    def add_incoming_flow(self, flow):
        self.incoming_flows.append(flow)

    def print_process(self):
        print(self.name + ", " + self.path_to_file + ", " + self.iterate_outgoing_flows() + ", "
              + self.iterate_incoming_flows())

    def iterate_incoming_flows(self):
        ret_string = ""
        for i in self.incoming_flows:
            ret_string += '"' + i.from_process.name + "." + i.name + '", '
        ret_string = ret_string[:-2]
        return ret_string

    def iterate_outgoing_flows(self):
        ret_string = ""
        for i in self.outgoing_flows:
            ret_string += i.name + " [num: " + str(i.enumeration) + " assets: " + i.iterate_assets() + "targets: " \
                          + i.to_process.name + "], "
        ret_string = ret_string[:-2]
        return ret_string

    def get_responsibilities(self):
        ret_str = ""
        out_assets = {}
        in_assets = {}
        forwarded = {}

        for f in self.outgoing_flows:
            for a in f.assets:
                out_assets[a.name] = a

        for f in self.incoming_flows:
            for a in f.assets:
                in_assets[a.name] = a

        for a in in_assets:
            if a not in out_assets:
                ret_str += "[" + a + " Store::],\n"
            else:
                forwarded[a] = a
                ret_str += "[" + a + " Forward:: " + a + "],\n"

        for x in out_assets:
            if a not in forwarded:
                ret_str += "[" + x + " Forward:: " + x + "],\n"

        ret_str = ret_str[:-2]
        return ret_str

    def set_asset_target(self):
        for f in self.incoming_flows:
            for a in f.assets:
                for f2 in self.outgoing_flows:
                    if a not in f2.assets:
                        a.targets.append(self.name)

    def iterate_assets(self):
        ret_string = ""

        for f in self.outgoing_flows:
            for a in f.assets:
                self.append_asset(a)

        for f in self.incoming_flows:
            for a in f.assets:
                self.append_asset(a)

        for a in self.assets:

            ret_string += a.name + ", "

        ret_string = ret_string[:-2]
        print(ret_string)
        return ret_string

    def append_asset(self, new_asset):
        if new_asset.name + new_asset.source.name not in self.asset_copy_tracker:
            self.assets.append(new_asset)
            self.asset_copy_tracker[new_asset.name + new_asset.source.name] = new_asset

# [num: 10 assets: ModifiedList targets: WriteList]
