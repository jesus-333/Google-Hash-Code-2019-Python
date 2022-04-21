import numpy as np

from support_data_extraction import get_file, extract_info, clean_target

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets
from support_solution import compilationTree
from support_solution_networkx import compilationTreeNX, clean_solution

import matplotlib.pyplot as plt

#%%

debug_var = True

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

# Variable that indicate if there are extra server. 
# N.b. Each server is dedicated to a single target but there can been more server that target. 
# This variable is used to track the free server in this situations
# 1 = free server, 0 = server assign to a target
free_server = np.ones(S)
free_server[0:len(target)] = 0

# Replication list
replication_list = []

while(True):
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Replication process
    
    idx_to_remove = []
    for i in range(len(replication_list)):
        # Reduce by 1 the replication time for the current file
        replicating_file = replication_list[i]
        files_info[replicating_file]['r'] -= 1
        
        # If the file has finish the replication
        if(files_info[replicating_file]['r'] <= 0):
            # Save the position in the replication list to remove it
            idx_to_remove.append(i)
            
            # Check if the file is currently compiling and remove it
            for idx_server in range(S):
                current_elaboration[idx_server] == replicating_file
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # File selection
    
    for idx_server in range(S):
        idx_choosen_file = -1
        
        # If the server has finish the compilation of the current file and it IS NOT free
        if(server_to_done[idx_server] == 1 and free_server[idx_server] == 0):
            # Extract leaf (files with no dependecies) from the tree
            possible_files = compilation_tree_list[idx_server].leaf_list
            
            if(len(possible_files) == 0): # If I have only a 0 leaf this mean that I have finish the compilation of the target and server is completely free 
                server_to_done[idx_server] = 0
                free_server[idx_server] = 1
                pass
            elif(len(possible_files) == 1): # If I have only 1 leaf (file) I'm forced to select it
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
                        idx_choosen_file = j
                
                # Choose the files with the minor compilation time if for some reason no files has been selected
                # This can happen if all the leaf are currently compilating/replicating
                # TODO choose the file with the highest replication time
                if(idx_choosen_file == -1): idx_choosen_file = 0
            
            # Start compiling the selected file
            selected_file = possible_files[idx_choosen_file]

        
        # If the server has finish the compilation of the current file and it IS free
        if(server_to_done[idx_server] == 1 and free_server[idx_server] == 1):
            # Choose the leaf (file) with the highest compilation time between all the files available
            
            # Create the list of all the leaf
            possible_files = []
            for tmp_compilation_tree in compilation_tree_list: possible_files += tmp_compilation_tree.leaf_list
            
            # Sort the list by compilation time (from higher to lower) and choose the first file
            possible_files_sorted = sorted(possible_files, key=lambda x: files_info[x]['c'], reverse = True)
            selected_file = possible_files[0]
            
            
        
        if(idx_choosen_file != -1):
            # Start compiling the selected file
            current_elaboration[idx_server] = selected_file
            time_for_current_elaboration[idx_server] = files_info[selected_file]['c']
            server_to_done[idx_server] = 0
            
            # Update solution string
            solution_string += "{} {}\n".format(current_elaboration[idx_server], idx_server) # Update solution string
            
            if(debug_var): print(t, "Server: {} - File choosen: {}".format(idx_server, selected_file))
            
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    
    t += 1
    time_for_current_elaboration -= 1
    
    if(t > 2): break

