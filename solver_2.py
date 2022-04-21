import numpy as np

from support_data_extraction import get_file, extract_info, clean_target

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets
from support_solution import compilationTree
from support_solution_networkx import compilationTreeNX

import matplotlib.pyplot as plt

#%%

idx_file = 0

# Load the data
data = get_file()

# Extract info
C, T, S, files_info, targets_raw = extract_info(data[idx_file])
files_info_backup = extract_info(data[idx_file])[3]
targets = clean_target(targets_raw, files_info)
print("Total targets: ", len(targets_raw))
print("Achievable targets: ", len(targets))


# Sort targets by attribute. Targets is intended as the target file to compile
# attribute = 'points' 
attribute = 'deadline'
targets = sort_target_by_attribute(targets, attribute)  

#%%

# Visualize a compilation tree of a target (For debugging)
targets_keys = list(targets.keys())

# Create the compilation tree for each target file
compilation_file_list_per_target = create_compilation_tree_per_targets(files_info, targets)

compilation_tree_list = [compilationTreeNX(target, compilation_file_list_per_target[target], files_info) for target in targets]
compilation_tree_dict = {}
for target in targets: compilation_tree_dict[target] = compilationTreeNX(target, compilation_file_list_per_target[target], files_info)

tmp_tree = compilation_tree_list[0]

#%%


solution_string = ""

# Time variable
t = 0

# List of files compiled in each server
files_compiled_per_server = [[] for _ in range(S)]

# Files currently compiling in each server
current_elaboration = [None for _ in range(S)]

# Time remaining for the compilation of each file
time_for_current_elaboration = np.zeros(S)

# Vector that indicate wich file have finish the compilation of the current file. 1 = Finish, 0 = Currently compiling
server_to_done = np.ones(S)

# Replication list
replication_list = []

while(True):
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # File selection
    
    for i in range(S):
        # If the server has finish the compilation of the current file
        if(server_to_done[i]):
            # Extract leaf (files with no dependecies) from the tree
            possible_files = compilation_tree_list[i].leaf_list
            
            if(len(possible_files) == 1): # If I have only a single leaf (file) I'm forced to select it
                idx_choosen_file = 0
            else: # Case with multiple leaf
            
                # Sort leaf by compilation time
                possible_files_sorted = sorted(possible_files, key=lambda x: files_info[x]['c'], reverse = False)
                
                # Select the file with the minor compilation time that is not replicating or compiling
                for j in range(len(possible_files_sorted)):
                    file = possible_files_sorted[j]
                    if file in current_elaboration: pass
                    elif file in replication_list: pass
                    else:
                        idx_choosen_file = i
                        
            current_elaboration[i] = possible_files[0]
            time_for_current_elaboration[i] = files_info[possible_files[0]]['c']
            server_to_done[i] = 0
                        
            
            
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    t += 1
    time_for_current_elaboration -= 1
    
    if(t > 20): break

