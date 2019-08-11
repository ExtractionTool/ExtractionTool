from SecTool.model import Process, Flow, Asset
import re
import glob
import os
from pathlib import Path

global_flows = {}

running_dir = os.getcwd()
print(running_dir)
extracted_SecDFD_destination = running_dir
extracted_SecDFD_name = "mySecDFD.mydsl"

default_src_java_path = running_dir
default_dot_file_repo_path = running_dir

keywords_file = open(os.path.join(running_dir, "keywords.txt"), "r")
keywords_arr = keywords_file.read().split(",")
home_repo_path = running_dir
graph_repo_path = running_dir
home_dot_path = running_dir


# -----------------------------------------------------------------------
#              USER INTERACTION AND VARIABLE SPECIFICATION
# -----------------------------------------------------------------------

chosen_src_home_path = input("Please input the complete path to the folder of the project you wish to "
                             "analyze: ")
home_repo_path = chosen_src_home_path

while not os.path.exists(home_repo_path):
    chosen_src_home_path = input("Looks like this path leads nowhere, please try again: ")
    home_repo_path = chosen_src_home_path


print("\n")
print("-------")
chosen_dot_file_repo_path = input("Please specify the path to the directory containing your .dot-files. This is the"
                                  "same as your Doxygen destination directory (the directory where Doxygen puts all"
                                  "the generated documentation), but with an added '/html'."
                                  "Write the path here: ")
home_dot_path = chosen_dot_file_repo_path

while not os.path.exists(home_dot_path):
    chosen_dot_file_repo_path = input("Looks like the path you wrote does not exist. Write the correct path here: ")
    home_dot_path = chosen_dot_file_repo_path

print("\n")
print("-------")
print("Default path to .mydsl-file target directory: " + extracted_SecDFD_destination)
print("(If this is your desired destination, copy the path and paste it in the next step)")
extracted_SecDFD_destination = input("Please specify the directory in which you want the generated SecDFD "
                                     "(the .mydsl file) to be saved: ")
while not os.path.exists(extracted_SecDFD_destination):
    extracted_SecDFD_destination = input("Path does not exist, please try again: ")

print("\n")
print("-------")
print("What would you like to name the file? Remember to begin with a lowercase letter,"
      " and to add the format (.mydsl).\n"
      "For example: mySecDFD.mydsl")
extracted_SecDFD_name = input("Enter the filename here: ")

print("Running...")


# -----------------------------------------------------------------------
#                       PROGRAM MAIN START
# -----------------------------------------------------------------------

os.chdir(home_dot_path)
array_of_paths_to_call_graph_files = []
for f in glob.glob("*cgraph.dot"):
    array_of_paths_to_call_graph_files.append(home_dot_path + "/" + f)

result_string = ""

for dirpath in array_of_paths_to_call_graph_files:
    if dirpath is not "":
        thisfile = open(dirpath, "r")
        result_string += thisfile.read()

cleaned_results_as_string = result_string

cleaned_results_as_string = cleaned_results_as_string.replace("\l", "")

array_of_results_as_words = re.findall(r"[\w']+", cleaned_results_as_string)
print(array_of_results_as_words)
assets = []
assets_by_name = []

nbr_of_flows = 0

global_processes = [None] * 1000
global_processes.insert(0, None)

global2_processes = {}

global_flow_enumeration = 1

asset_copy_tracker = {}
process_copy_tracker = {}
flow_copy_tracker = {}


def find_assets_by_function(process, function_name, dest_process):
    global assets, assets_by_name, asset_copy_tracker
    identified_assets = []

    if process.name == dest_process.name and process.path_to_file == dest_process.path_to_file:
        return []

    try:
        myfile = open(process.path_to_file, "r")
        text = myfile.read()
        result = re.search(function_name + "(.*){", text)
        if result is not None:
            results = result.group(1)
            results_as_array = re.findall(r"[\w']+", results)
            for k in keywords_arr:
                for r in results_as_array:
                    if k.lower() in r.lower() or k.lower() in function_name.lower():
                        asset_name = function_name + r.capitalize()

                        c_check_name = process.path_to_file + asset_name
                        if c_check_name not in asset_copy_tracker:
                            new_asset = Asset.Asset(asset_name, process, [], "[H C]")
                            new_asset.path = process.path_to_file
                            identified_assets.append(new_asset)
                            assets.append(new_asset)
                            asset_copy_tracker[c_check_name] = len(assets)-1

    except FileNotFoundError:
        print(process.path_to_file)
        print("ERROR: ")
        print("Oops! No such file.")

    return identified_assets


def specify_flow_from_node_id(node_id_from, node_id_to):
    global global_processes, global_flow_enumeration

    from_node = global_processes[node_id_from]
    to_node = global_processes[node_id_to]

    if from_node is None or to_node is None:
        print("---------------------------------------------------------------\n")
        print("ERROR: Some or all target nodes (processes) are unpopulated. ")
        print("Looks like the nodes aren't populated! This could be due to: \n"
              "1. No call-graphs as .dot-files being generated. Make sure you have \n"
              "   checked the boxes for generating call- and caller-graphs in Doxygen, \n"
              "   and that you have set DOT_CLEANUP to 'False'.\n"
              "2. The path you have specified to the folder where your .dot-files are\n"
              "   stored is wrong. Make sure the path you specify includes '/html'.\n"
              "3. Your keywords are too specific, meaning that no matches occur.\n")
        print("The unpopulated node(s) in question is/are: ")
        if from_node is None:
            print("Node: " + str(node_id_from))
        if to_node is None:
            print("Node: " + str(node_id_to))
    else:
        flow_assets = find_assets_by_function(from_node, from_node.func_name, to_node)

        comparative_name = from_node.name + from_node.func_name + from_node.path_to_file + to_node.name + to_node.func_name
        if len(flow_assets) is not 0:

            if comparative_name not in flow_copy_tracker:
                new_flow = Flow.Flow(from_node.name + from_node.func_name, from_node, to_node,
                                     global_flow_enumeration, flow_assets, False)
                flow_copy_tracker[comparative_name] = new_flow
                from_node.outgoing_flows.append(new_flow)
                to_node.incoming_flows.append(new_flow)
                global_flow_enumeration += 1
                global_flows[from_node.name] = new_flow
            else:
                flow_copy = flow_copy_tracker.get(comparative_name)
                flow_copy.assets.extend(flow_assets)
                from_node.outgoing_flows.append(flow_copy)
                to_node.incoming_flows.append(flow_copy)


def find_processes(results_as_array):
    global nbr_of_flows, global_processes
    for index, word in enumerate(results_as_array):
        if word == "label" and "Node" in results_as_array[index-1]:
            nbr_of_flows += 1
            sub_path = ""
            name = ""
            func_name = ""
            for j in range(index+1, len(results_as_array)):
                if results_as_array[j+1] == "height" or results_as_array[j+1] == "width":
                    func_name = results_as_array[j]
                    break
                name = results_as_array[j]
                sub_path += "/" + results_as_array[j]
            sub_path += ".java"

            complete_path = home_repo_path + sub_path
            for fullname in Path(home_repo_path).glob("**" + sub_path):
                complete_path = str(Path(fullname).resolve())

            if os.path.exists(complete_path):
                node_id = results_as_array[index - 1]
                comparative_name = complete_path  # sub_path # + func_name
                number = int(node_id.split("e")[1])

                if comparative_name in process_copy_tracker:
                    process_copy = process_copy_tracker.get(comparative_name)
                    global_processes.insert(number, process_copy)
                else:
                    proc = Process.Process(name, node_id, [], [], [], complete_path)
                    proc.func_name = func_name
                    process_copy_tracker[comparative_name] = proc
                    global_processes.insert(number, proc)

            elif not os.path.exists(complete_path):
                print("WARNING: ")
                print("Oops! Looks like we couldn't find the file. It could be because the home repository for \n"
                      "the source code was not correctly specified. Make sure to end the path you specify from \n"
                      "where the following path begins: " + sub_path)
                print("(OBS: Please note that this could also be due to the class being an internal class. In \n"
                      "this case, you can ignore this warning.)")


def find_flows(results_as_array):
    print(global_processes)
    for index, word in enumerate(results_as_array):
        if "Node" in word and "Node" in results_as_array[index - 1]:
            number1 = int(word.split("e")[1])
            number2 = int(results_as_array[index - 1].split("e")[1])
            specify_flow_from_node_id(number1, number2)


def create_secdfd(processes_arr):
    global extracted_SecDFD_destination, extracted_SecDFD_name

    os.chdir(extracted_SecDFD_destination)
    newtestfile = open(extracted_SecDFD_name, "w+")
    newtestfile.write("EDFD " + extracted_SecDFD_name.split(".")[0].capitalize() + "[\n")
    newtestfile.write(" assets:\n")
    for y in assets:
        newtestfile.write("     Asset " + y.name + " values: " + y.values + " source: " + y.source.name + " targets: ")
        for z in y.targets:
            newtestfile.write(z + ", ")
        newtestfile.write("\n")
    newtestfile.write(" elements:\n")

    for x in processes_arr:
        if not (len(x.incoming_flows) is 0 and len(x.outgoing_flows) is 0):
            newtestfile.write("     Process " + x.name + "[\n")
            newtestfile.write("         responsibilities: " + x.get_responsibilities() + "\n")
            newtestfile.write("         assets: " + x.iterate_assets() + "\n")
            newtestfile.write("         incoming flows: " + x.iterate_incoming_flows() + "\n")
            newtestfile.write("         outgoing flows: " + x.iterate_outgoing_flows() + "\n")
            newtestfile.write("     ], \n")

    newtestfile.write("]")

# -----------------------------------------------------------------------
#                       PROGRAM MAIN FINISH
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------
#                       PROGRAM EXECUTION
#                       *****************


find_processes(array_of_results_as_words)
find_flows(array_of_results_as_words)

global_processes = list(set(global_processes))
global_processes = filter(None, global_processes)

create_secdfd(global_processes)

# -----------------------------------------------------------------------

print("Run complete!")


