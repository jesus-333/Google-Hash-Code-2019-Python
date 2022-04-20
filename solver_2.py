import numpy as np

from support_data_extraction import get_file, extract_info

from support_solution import create_compilation_tree, sort_target_by_attribute, create_compilation_tree_per_targets
from support_solution import compilationTree

#%%

idx_file = 0

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

#%%

tmp_target = targets_keys[0]
tmp_tree = compilationTree(tmp_target, files_info)

leaf_list = tmp_tree.get_leaf()

print("Deleted leaf:\n",leaf_list[0], "\n\n")
del leaf_list[0]

leaf_list = tmp_tree.get_leaf(update = True)
for leaf in leaf_list: print(leaf)

