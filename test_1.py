import numpy as np

from support_data_extraction import get_file, extract_info

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets, 
from support_solution import clean_compilation_tree, extract_last_layers
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
show_layers( create_compilation_tree(files_info, tmp_target))

# Create the compilation tree for each target file
compilation_tree_per_target = create_compilation_tree_per_targets(files_info, targets)


#%%

solution_string = ""

# Time variable
t = 0

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
server_to_do = np.ones(S)
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


# Fill the remaining servers. The files to compile are chosen by 

for j in range(S - len(current_elaboration)):
    current_elaboration[i]
    

# Delete i variable (for safety)
del i


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# while(True):
#     t += 1