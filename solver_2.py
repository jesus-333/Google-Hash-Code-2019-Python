import numpy as np

from support_data_extraction import get_file, extract_info, clean_target

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets
from support_solution import compilationTree
from support_solution_networkx import compilationTreeNX, clean_solution, clean_dependency

import matplotlib.pyplot as plt

#%%

debug_var = True

idx_file = 5

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
targets = sort_target_by_attribute(targets, attribute, reverse = False) 
targets_keys = list(targets.keys()) 

#%%

# Visualize a compilation tree of a target (For debugging)
targets_keys = list(targets.keys())

# Create the compilation tree for each target file
compilation_file_list_per_target = create_compilation_tree_per_targets(files_info, targets)

compilation_tree_dict = {}
for target in targets: compilation_tree_dict[target] = compilationTreeNX(target, compilation_file_list_per_target[target], files_info)

# compilation_tree_list = [compilationTreeNX(target, compilation_file_list_per_target[target], files_info) for target in targets]

compilation_tree_list = []
for idx_server in range(S): 
    target_file = targets_keys.pop(0)
    compilation_tree_list.append(compilationTreeNX(target_file, compilation_file_list_per_target[target_file], files_info))
    
    del compilation_tree_dict[target_file]
    
    if(debug_var): print(0, "\tServer: {} - NEW Target assign: {}".format(idx_server, target_file))
    
    # Stop if I have more server than target
    if(idx_server >= len(targets) - 1): break

# Used for debug
tmp_tree = compilation_tree_list[0]
compilation_tree_dict_backup = {}
for target in targets: compilation_tree_dict_backup[target] = compilationTreeNX(target, compilation_file_list_per_target[target], files_info)

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
server_to_do = np.ones(S)

# Variable that indicate if there are extra server. 
# N.b. Each server is dedicated to a single target but there can been more server that target. 
# This variable is used to track the free server in this situations
# 1 = free server, 0 = server assign to a target
free_server = np.ones(S)
free_server[0:len(targets)] = 0

# Replication list
replication_list = []

while(True):
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # File REPLICATION 
    
    file_to_remove = []
    for replicating_file in replication_list:
        # Reduce by 1 the replication time for the current file
        files_info[replicating_file]['r'] -= 1
        
        # If the file has finish the replication
        if(files_info[replicating_file]['r'] <= 0):
            # Save the current file to remove it from the replication list since it has finish replication
            file_to_remove.append(replicating_file)
            
            # Check if the file is currently compiling and eventually remove it
            for idx_server in range(S):
                # If the file is currently compiling then stop the compilation
                if(current_elaboration[idx_server] == replicating_file):
                    # Remove the selection/compilation of the file from the solution
                    # Since it is replicated it is available for all the server
                    solution_string = clean_solution(solution_string, replicating_file, idx_server)
                    
                    # Set the server as available for compilation
                    server_to_do[idx_server] = 1
                    
                    # Set the variable to nonsensical value (for safety) 
                    current_elaboration[idx_server] = ''
                    time_for_current_elaboration[idx_server] = -1
                    
            # Remove the file from all the compilation tree (if it exist in the compilation tree) currently in the server
            for compilation_tree in compilation_tree_list: 
                # Check if the node (file) exist
                if(replicating_file in compilation_tree.G.nodes()):
                    # If it exist remove the node
                    compilation_tree.remove_file(replicating_file)
            
            # Remove the file from the compilation tree not in the server
            for target in targets_keys:
                compilation_tree = compilation_tree_dict[target]
                if(replicating_file in compilation_tree.G.nodes()): compilation_tree.remove_file(replicating_file)
            
            # Remove the file from the dependencies of all the file
            clean_dependency(replicating_file, files_info)
            
            # Add the file to the compiled file of all the server
            for idx_server in range(S): 
                files_compiled_per_server[idx_server].append(replicating_file)
                files_compiled_per_server[idx_server] = list(set(files_compiled_per_server[idx_server]))
            
            if(debug_var): print(t, "\tFinish REPLICATION File: {}\n".format(replicating_file))
            
    # Remove the file that has finish replication
    for file in file_to_remove: replication_list.remove(file)

                
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # File SELECTION
    
    for idx_server in range(S):
        idx_choosen_file = -1
        
        # If the server has finish the compilation of the current file and it IS NOT free
        # Choose the leaf (file) with the minor compilation time that is not compiling (in any server) or replicating 
        # If all the leaf (file) are currently compiling/replicating choose the one with the lowest compilation time
        # In this case there cannot be dependency problem because each server is paired with a specific compilation tree
        if(server_to_do[idx_server] == 1 and free_server[idx_server] == 0):
            if(debug_var and current_elaboration[idx_server] != ''): print(t, "\tServer: {} - File END: {}".format(idx_server, current_elaboration[idx_server]))
            
            if(t != 0): 
                # N.B. Due to the replication process some file can be removed early from the compilation tree while they are compiling.
                # When this happen the server is set as free for new file to compile so it return in this section of the code
                # So the check avoid to remove node (files) that are alredy been removed by the replication process
                if(current_elaboration[idx_server] != ''):
                    # Add the file to the replication list
                    if current_elaboration[idx_server] not in replication_list: replication_list.append(current_elaboration[idx_server])
                    
                    # Add the files to the compiled file in the server
                    files_compiled_per_server[idx_server].append(current_elaboration[idx_server])
                    
                    # Remove the file from the current compilation tree
                    compilation_tree_list[idx_server].remove_file(current_elaboration[idx_server])
            
            # Extract leaf (files with no dependecies) from the tree
            possible_files = compilation_tree_list[idx_server].leaf_list
            
            if(len(possible_files) == 0): # If I have only a 0 leaf this mean that I have finish the compilation of the target and server is free for new target or support work
                del targets[current_elaboration[idx_server]]    
                if(debug_var): print(t, "\t\tTarget complete")
            
                if(len(targets_keys) > 0): # If there are more targets available assign the new target to the server
                    target_file = targets_keys.pop(0)
                    compilation_tree_list[idx_server] = compilation_tree_dict[target_file] 
                    if(debug_var): print(t, "\tServer: {} - NEW Target assign: {}".format(idx_server, target_file))
                    
                    # Clean the new compilation tree of the file already compiled in the server
                    for compiled_file in files_compiled_per_server[idx_server]:
                        if(compiled_file in compilation_tree_list[idx_server].G.nodes()): compilation_tree_list[idx_server].remove_file(compiled_file)
                    
                    # Same step done below for the case with multiple leaf. Read the comment in that section
                    possible_files = compilation_tree_list[idx_server].leaf_list
                    possible_files_sorted = sorted(possible_files, key=lambda x: files_info[x]['c'], reverse = False)
                    for j in range(len(possible_files_sorted)):
                        file = possible_files_sorted[j]
                        if file in current_elaboration: pass
                        elif file in replication_list: pass
                        else: idx_choosen_file = j
                    if(idx_choosen_file == -1): idx_choosen_file = 0
                    idx_choosen_file = possible_files.index(possible_files_sorted[idx_choosen_file])

                    
                    server_to_do[idx_server] = 0
                    
                else: # If there aren't any new target set the server as free and use it for support task
                    if(len(targets) == 0): break # In this case I also finish the target so I stop here
                    else: free_server[idx_server] = 1 # Otherwise set the server as free
                
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
                    else: idx_choosen_file = j
                        
                
                # Choose the files with the minor compilation time if for some reason no files has been selected
                # This can happen if all the leaf are currently compilating/replicating
                # TODO choose the file with the highest replication time
                if(idx_choosen_file == -1): idx_choosen_file = 0
                
                # Find the index of the file in non sorted list
                idx_choosen_file = possible_files.index(possible_files_sorted[idx_choosen_file])
            
            # Start compiling the selected file
            if(idx_choosen_file != -1): selected_file = possible_files[idx_choosen_file]

        
        # If the server has finish the compilation of the current file and it IS free
        # Choose the leaf (file) with the highest compilation time between all the files available and all the dependencies ok
        if(server_to_do[idx_server] == 1 and free_server[idx_server] == 1):
            if(debug_var and current_elaboration[idx_server] != ''): print(t, "\tServer: {} - File END: {}".format(idx_server, current_elaboration[idx_server]))
            
            # Add the files to the compiled file in the server
            files_compiled_per_server[idx_server].append(current_elaboration[idx_server])
            
            # Create the list of all the leafs
            possible_files = []
            for tmp_compilation_tree in compilation_tree_list: possible_files += tmp_compilation_tree.leaf_list
            
            # Sort the list by compilation time (from higher to lower) and choose the first file
            possible_files_sorted = sorted(possible_files, key=lambda x: files_info[x]['c'], reverse = True)
            
            for j in range(len(possible_files_sorted)):
                # Currently analyzed file
                tmp_file = possible_files_sorted[j]
                
                # If file has no dependency there are no problem so the file is selected
                if(len(files_info[tmp_file]['dependencies_list']) == 0):
                    idx_choosen_file = j
                    break
                else:
                    # Check if all the dependencies are ok
                    # The condition inside the if is true only if all element of list 1 (dependencies_list) are inside the list 2 (list of compiled files of the server)
                    if(all(file in files_info[tmp_file]['dependencies_list'] for file in files_compiled_per_server[idx_server])):
                        idx_choosen_file = j
                        break
                    else: # If not skip the server for the current iteration
                        pass
                
            selected_file = possible_files_sorted[idx_choosen_file]
            
        
        if(idx_choosen_file != -1):
            # Start compiling the selected file
            current_elaboration[idx_server] = selected_file
            time_for_current_elaboration[idx_server] = files_info[selected_file]['c']
            server_to_do[idx_server] = 0
            
            # Update solution string
            solution_string += "{} {}\n".format(current_elaboration[idx_server], idx_server) # Update solution string
            
            if(debug_var): print(t, "\tServer: {} - File CHOOSEN: {}\n".format(idx_server, selected_file))
            
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    t += 1
    time_for_current_elaboration -= 1
    
    # Check the server that has finish the compilation of the current file and set their flag to 1
    server_to_do[np.where(time_for_current_elaboration <= 0)[0]] = 1
    
    # Condition to finish the cycle
    # A target is removed from the list only when it is compiled. So the cycle finish only when all the target are compiled
    if(len(targets) == 0): break

    # if(t > 30): break

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

