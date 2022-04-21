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
C, T, S, files_info, targets = extract_info(data[idx_file])
files_info_backup = extract_info(data[idx_file])[3]


# Sort targets by attribute. Targets is intended as the target file to compile
# attribute = 'points' 
attribute = 'deadline'
targets = sort_target_by_attribute(targets, attribute)  

#%%

# Visualize a compilation tree of a target (For debugging)
targets_keys = list(targets.keys())

# Create the compilation tree for each target file
compilation_tree_per_target = create_compilation_tree_per_targets(files_info, targets)

tmp_target_key = targets_keys[0]
tmp_target_compilation_list = compilation_tree_per_target[tmp_target_key]

#%%

# tmp_tree = compilationTree(tmp_target, files_info)
# tmp_tree = compilationTree('c1cx', files_info)

# print("Leaf list BEFORE:\n", tmp_tree.get_leaf(update = True))
# print("\nDeleted leaf c1")
# print(tmp_tree.remove_leaf('c1'))
# print("Leaf list AFTER\n", tmp_tree.get_leaf(update = True))

#%%

tmp_tree = compilationTreeNX(tmp_target_key, tmp_target_compilation_list, files_info)

tmp_tree.draw(figsize = (10, 5))
tmp_tree.update_adjacency_matrix(True)
tmp_adj_mat = tmp_tree.adj_mat

tmp_node_list = list(tmp_tree.G.nodes())
