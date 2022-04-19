import numpy as np

from support_data_extraction import get_file, extract_info

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets
from support_solution import clean_compilation_tree, choose_file_by_compilation_time
from support_solution import compute_layers_string, show_layers

#%%

# Load the data
data = get_file()

# Extract info
C, T, S, files_info, targets = extract_info(data[0])

# Sort targets by attribute. Targets is intended as the target file to compile
# attribute = 'points' 
attribute = 'deadline'
targets = sort_target_by_attribute(targets, attribute)  

#%%

# Visualize a compilation tree of a target (For debugging)
targest_keys = list(targets.keys())
tmp_target = targest_keys[0]
# show_layers(create_compilation_tree(files_info, tmp_target))

# Create the compilation tree for each target file
compilation_tree_per_target = create_compilation_tree_per_targets(files_info, targets)


#%%

solution_string = ""

# Time variable
t = 0

#
files_compiled_per_server = [[] for _ in range(S)]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Find the first files to compile

# Variable to save the current files in compilation 
current_elaboration = [None for _ in range(S)]
time_for_current_elaboration = np.zeros(S)
tmp_compilation_tree_list = []
i = 0

# Select the first S targets (N.B. It select and entire compilation trees)
tmp_target_to_remove = []
for target in targets:
    tmp_compilation_tree_list.append(compilation_tree_per_target[target] + [])
    i += 1
    tmp_target_to_remove.append(target)
    
    if(i >= S): break

for target in tmp_target_to_remove: del targets[target]

# Delete variables (for safety)
del i, tmp_target_to_remove

# Chcek if there are "last layer" with only 1 file in the various compilation tree
# If there are, for that tree I'm forced to start the compilation from that file
server_to_do = np.ones(S) # Variable that check which servers are assigned (0 = assigned, 1 = not assigned)
i = 0
for tmp_compilation_tree in tmp_compilation_tree_list:
    if(len(tmp_compilation_tree[-1]) == 1): 
        # Remove the file from the compilation tree
        tmp_file = tmp_compilation_tree[-1].pop(0)
        
        # Add the file to the files list that are current compilating
        current_elaboration[i] = tmp_file
        time_for_current_elaboration[i] = files_info[tmp_file]['c']
        solution_string += "{} {}\n".format(tmp_file, i)
        server_to_do[i] = 0
        
    i += 1

# Delete i variable (for safety)
del i


# Fill the remaining servers. The files to compile are chosen by 
# Remember that each compilation tree is assigned to a server. The first element of tmp_compilation_tree_list is assigned to server 1 etc etc.
idx_server_to_do = np.where(server_to_do == 1)[0]
for i in range(len(idx_server_to_do)):
    # Select the server to do
    idx_server = idx_server_to_do[i]
    # print(idx_server)
    
    # Choose the last layer for the compilation tree assigned to that server
    tmp_layer = tmp_compilation_tree_list[idx_server][-1]
    
    # Select the file with the minor compilation time
    tmp_file = choose_file_by_compilation_time(tmp_layer, files_info)
    
    # Assign the file to the server
    current_elaboration[idx_server] = tmp_file
    time_for_current_elaboration[i] = files_info[tmp_file]['c']
    solution_string += "{} {}\n".format(tmp_file, i)
    server_to_do[i] = 0
    
    # Condition needed if there are more servers than compilation tree
    # In case I have more server FOR NOW I LEFT SOME SERVER SLEEP
    if(idx_server >= len(tmp_compilation_tree_list)): break


for compilation_tree in tmp_compilation_tree_list: clean_compilation_tree(compilation_tree)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# List that contain all the files to replicate
files_to_replicate_list = []

while(True):
    # Increase time
    t += 1
    
    # Reduce current elaboration time by 1
    time_for_current_elaboration -= 1
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    # Replication process
    idx_to_remove = []
    for j in range(len(files_to_replicate_list)):
        file = files_to_replicate_list[j]
        
        # Decrease time needed
        files_info[file]['r'] -= 1
        
        # If I finisg a replication 
        if(files_info[file]['r'] <= 0): 
            # Set the replicated flag to True
            files_info[file]['replicated'] = True
            
            # Add the file to the list of compiled flag for the server
            for files_compiled in files_compiled_per_server: 
                if file not in files_compiled: files_compiled.append(file)
            
            # N.b. the two operation are redundant in some way. TODO improve mantaining only 1
            
            idx_to_remove.append(j)
    
    # Remove the element from the replication list
    idx_to_remove.reverse()
    for idx in idx_to_remove: files_to_replicate_list.pop(idx)
    
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    # Check if any file has finish to compile
    if(np.any(time_for_current_elaboration <= 0)):
        # Find the file(s) that has finished
        idx_server_to_do = np.where(time_for_current_elaboration == 1)[0]
        
        for i in range(len(idx_server_to_do)):
            idx_server = idx_server_to_do[i]
            finish_file = current_elaboration[idx_server]
            
            # Add the files to the current files compiled in that server
            files_compiled_per_server[idx_server].append(current_elaboration[finish_file])
            
            # Check if I am already replicating the file. If not add to the replication files list
            if(files_info[finish_file]['replicated'] == False and finish_file not in files_to_replicate_list):
                files_to_replicate_list.append(files_to_replicate_list)
            
            
            # Choose the last layer, Select the file with the minor compilation time, Assign the file to the server
            tmp_layer = tmp_compilation_tree_list[idx_server][-1]
            tmp_file = choose_file_by_compilation_time(tmp_layer, files_info)
            current_elaboration[idx_server] = tmp_file
            time_for_current_elaboration[i] = files_info[tmp_file]['c']
            solution_string += "{} {}\n".format(tmp_file, i)
            
        
    if(t > 20): break
    