import numpy as np

from support_data_extraction import get_file, extract_info

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets
from support_solution import compute_layers_string, show_layers

#%%

# Load the data
data = get_file()

# Extract info
C, T, S, files_info, targets = extract_info(data[0])

# Sort target by attribute
attribute = 'points' 
# attribute = 'deadline'
targets = sort_target_by_attribute(targets, attribute)

#%%

# Visualize a compilation tree of a target (For debugging)
targest_keys = list(targets.keys())
tmp_target = targest_keys[0]
show_layers( create_compilation_tree(files_info, tmp_target))

# Create the compilation tree for each target file
compilation_tree_per_target = create_compilation_tree_per_targets(files_info, targets)


#%%


# Time variable
t = 0

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Find the first file to compile

# Variable to save the current files in compilation 
current_elaboration = []
tmp_compilation_tree_list = []
i = 0

# Select the first S targets
for target in targets:
    tmp_compilation_tree_list.append(compilation_tree_per_target[target] + [])
    i += 1
    
    if(i >= S): break

# Delete i variable (for safety)
del i

# Chcek if there are "last layer" with only 1 file in the various compilation tree
# If there are for that tree I'm forced to start the compilation from that file
for tmp_compilation_tree in tmp_compilation_tree_list:
    if(len(tmp_compilation_tree[-1]) == 1): current_elaboration.append(tmp_compilation_tree[-1][0])
    
for i in range(S - len(current_elaboration)):

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# while(True):
#     t += 1