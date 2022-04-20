import numpy as np

from support_data_extraction import get_file, extract_info

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets
from support_solution import clean_compilation_tree, choose_file_by_compilation_time, remove_file_from_dependecies_list, check_compilation_trees
from support_solution import compute_layers_string, show_layers

#%%

idx_file = 5

# Load the data
data = get_file()

# Extract info
C, T, S, files_info, targets = extract_info(data[idx_file])
files_info_backup = extract_info(data[idx_file])[3]


# Sort targets by attribute. Targets is intended as the target file to compile
# attribute = 'points' 
attribute = 'deadline'
targets = sort_target_by_attribute(targets, attribute)  

#%%

# Visualize a compilation tree of a target (For debugging)
targets_keys = list(targets.keys())
tmp_target = targets_keys[0]
# show_layers(create_compilation_tree(files_info, tmp_target))

# Create the compilation tree for each target file
compilation_tree_per_target = create_compilation_tree_per_targets(files_info, targets)


#%% Selection of the first file

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
    
    # Condition needed if there are more servers than compilation tree
    # In case I have more server FOR NOW I LEFT SOME SERVER SLEEP
    if(idx_server >= len(tmp_compilation_tree_list)): break
    
    # Choose the last layer for the compilation tree assigned to that server
    tmp_layer = tmp_compilation_tree_list[idx_server][-1]
    
    # Select the file with the minor compilation time
    tmp_file = choose_file_by_compilation_time(tmp_layer, files_info)
    
    # Assign the file to the server
    current_elaboration[idx_server] = tmp_file
    time_for_current_elaboration[i] = files_info[tmp_file]['c']
    solution_string += "{} {}\n".format(tmp_file, i)
    server_to_do[i] = 0


for compilation_tree in tmp_compilation_tree_list: clean_compilation_tree(compilation_tree)

del idx_server_to_do

print("Initial setup:")
print("\t {} Current compilation list".format(current_elaboration))
print("\t {} Current compilation time".format(time_for_current_elaboration))

#%% Compilation cycle

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# List that contain all the files to replicate
files_to_replicate_list = []

while(True):
    # Increase time
    t += 1
    
    # Reduce current elaboration time by 1
    time_for_current_elaboration -= 1
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # REPLICATION process
    
    idx_to_remove = []
    for j in range(len(files_to_replicate_list)):
        file_to_replicate = files_to_replicate_list[j]
        
        # Decrease time needed
        files_info[file_to_replicate]['r'] -= 1
        
        # If I finisg a replication 
        if(files_info[file_to_replicate]['r'] <= 0): 
            print(t, "\tFinish replication files: ", file_to_replicate)
            
            # Set the replicated flag to True
            files_info[file_to_replicate]['replicated'] = True
            
            # Add the file to the list of compiled flag for the server
            for files_compiled in files_compiled_per_server: 
                if file_to_replicate not in files_compiled: files_compiled.append(file_to_replicate)
            
            # Remove the file from the dependecies list of all files since it is replicated
            remove_file_from_dependecies_list(file_to_replicate, files_info)
            
            # Check if the file is compiling somewhere and eventually remove it
            if(file_to_replicate in current_elaboration): idx_server_to_do = [i for i, x in enumerate(current_elaboration) if x == file_to_replicate]
            else: idx_server_to_do = []
            for idx in idx_server_to_do: time_for_current_elaboration[idx] = 0
            del idx_server_to_do
            
            idx_to_remove.append(j)
    
    # Remove the element from the replication list
    idx_to_remove.reverse() # Reverse the list to avoid problem with indices
    for idx in idx_to_remove: files_to_replicate_list.pop(idx)
    
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # COMPILATION process
    
    # Check if any file has finish to compile
    if(np.any(time_for_current_elaboration <= 0)):
        # Find the file(s) that has finished
        idx_server_to_do = np.where(time_for_current_elaboration <= 0)[0]
        
        for i in range(len(idx_server_to_do)):
            idx_server = idx_server_to_do[i]
            finish_file = current_elaboration[idx_server]
            print()
            if(time_for_current_elaboration[idx_server] >= 0):
                print(t, "\tServer:", idx_server_to_do[i], " - Finish compilation file: ", finish_file)
            
            # Add the files to the current files compiled in that server
            files_compiled_per_server[idx_server].append(current_elaboration[idx_server])
            
            # Check if the file is a target and eventualy remove it
            # This can happen if some target are inside the compilation tree of other target
            if(finish_file in targets.keys()): 
                del targets[finish_file]
                print(t, "\tTARGET {} - early removal".format(finish_file))
            
            # Check if I am already replicating the file. If not add to the replication files list
            if(files_info[finish_file]['replicated'] == False and finish_file not in files_to_replicate_list):
                files_to_replicate_list.append(finish_file)
    else:
        # If not files has finish compilation to prevent error during execution the list of servers that has finish elaboration is created as an empty list
        # In this way the cycle that iterate though the server for the selection of new file perform no iteration
        idx_server_to_do = []
            
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # SELECTION new file 
    
    for i in range(len(idx_server_to_do)):
        idx_server = idx_server_to_do[i]
        
        tmp_layer_backup = []
        while(True):
            # Check if the compilation tree is empty. This can happen if I finish the target and the file currently compiling is one of the last
            if(len(tmp_compilation_tree_list[idx_server]) == 0): break
            
            # Choose the last layer, Select the file with the minor compilation time
            tmp_layer = tmp_compilation_tree_list[idx_server][-1]
            tmp_file = choose_file_by_compilation_time(tmp_layer, files_info)
            file_is_good = False
            print("\tServer:", idx_server, "\tPossible new file: ", tmp_file)
            
            # Check if the file is not replicated
            if(files_info[tmp_file]['replicated'] == False): 
                # Check if the file is currently replicating
                if(tmp_file in files_to_replicate_list):
                    # Select the files only if the remaining replication time is higher than the current compilation time 
                    if(files_info[tmp_file]['r'] > files_info[tmp_file]['c']): 
                        file_is_good = True
                        print("\t\t", tmp_file, "SELECT for replication time reason (r = {}, c = {})".format(files_info[tmp_file]['r'], files_info[tmp_file]['c']))
                    else: 
                        print("\t\t", tmp_file, "REFUSE for replication time reason")
                    
                    # Check dependencies of the file
                    if(len(files_info[tmp_file]['dependencies_list']) == 0): # IF it has no dependencies it is ok
                        file_is_good = True
                        print("\t\t", tmp_file, "DEPENDECIES OK")
                    else: # If it has dependencies check if they are compiled in the server 
                        for dependency_file in files_info[tmp_file]['dependencies_list']: # Iterate through files
                            if(dependency_file not in files_compiled_per_server[idx_server]): # PROBLEM. The file needed is not in the compiled files
                                file_is_good = False
                                print("\t\t", tmp_file, "DEPENDECIES PROBLEM")
                                
                                # Save the current file since it cannot be compiled
                                tmp_layer_backup.append(tmp_file)
                else: # In this case the file is not replicated and is not replicating (i.e. it has not yet been compiled by any server)
                    file_is_good = True
                    print("\t\t", tmp_file, "NOT REPLICATING")
            
            else: # In this case the file is already duplicated
                file_is_good = False
                print("\t\t", tmp_file, "REFUSE because already replicated (replicated flag = {})".format(files_info[tmp_file]['replicated']) )
            
            # If the checks are passed select the file for the compilation and pass to the next server
            if(file_is_good): 
                current_elaboration[idx_server] = tmp_file # Set the file to compile
                time_for_current_elaboration[idx_server] = files_info[tmp_file]['c'] # Set the time for the current compilation
                solution_string += "{} {}\n".format(tmp_file, idx_server) # Update solution string
                clean_compilation_tree(tmp_compilation_tree_list[idx_server]) # Check and eventually clean the layer
                
                print("\t\t {} SELECTED for compilation".format(tmp_file))
                print("\t\t\t {} Current compilation list".format(current_elaboration))
                print("\t\t\t {} Current compilation time".format(time_for_current_elaboration))
                break
            else: # If file is not selected add it to the backup layer so it can be reinserted again in the current layer
                print("\t\t", tmp_file, "Inserted in backup layer")
                tmp_layer_backup.append(tmp_file)
                
            # Check if files remaining in th current layer. 
            if(len(tmp_layer) <= 0): 
                if(len(tmp_layer_backup) == 0): 
                    # If the backup layer is empty it means that there were no problem with dependencies
                    # So I can clean the layer since all the files are correctly compiled and proced with other layers
                    clean_compilation_tree(tmp_compilation_tree_list[idx_server])
                else:
                    # If the backup layer is NOT empty this means that some files were discarded because of some dependecies problem.
                    # This means that the files were not compiled. So for this iteration I not assign any file to the server
                    tmp_compilation_tree_list[idx_server][-1] = tmp_layer_backup
                    break
            
            
            # Check if layers remain for the current compilation tree. If not assign a new compilation tree
            if(len(tmp_compilation_tree_list[idx_server]) == 0):
                if(len(targets) > 0): # Check if there are new targets
                    # Take the first element in the target dictionary 
                    new_target = list(targets.items())[0][0]
                    
                    # Assign the new compilation tree to the current server
                    tmp_compilation_tree_list[idx_server] = compilation_tree_per_target[new_target] + []
                    del targets[new_target]
                    
        # CHECK OUTSIDE the while(True) search for new file
        # Check if layers remain for the current compilation tree. If not assign a new compilation tree
        if(len(tmp_compilation_tree_list[idx_server]) == 0):
            if(len(targets) > 0): # Check if there are new targets
                # Take the first element in the target dictionary 
                new_target = list(targets.items())[0][0]
                
                # Assign the new compilation tree to the current server
                tmp_compilation_tree_list[idx_server] = compilation_tree_per_target[new_target] + []
                del targets[new_target]
        
            
    # If the targets list is empty and also the compilation tree are empty I finish compilation
    if(len(targets) == 0 and np.sum(time_for_current_elaboration) <= 0): break
    # if(t > 1): break    

solution_string = str(len(solution_string.strip().split("\n"))) + "\n" + solution_string
text_file = open("solution.txt", "w")
n = text_file.write(solution_string)
text_file.close()

#%%

print("\n\n")
print(solution_string)

from solchecker import loadInstance, loadSolution, evalCheck

file_list = ['a_example.in', 'b_narrow.in', 'c_urgent.in', 'd_typical.in', 'e_intriguing.in', 'f_big.in']

instance = loadInstance("final_round_2019/{}".format(file_list[idx_file]))
solution = loadSolution("solution.txt", instance)
print("Score =", evalCheck(instance, solution))