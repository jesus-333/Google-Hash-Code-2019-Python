import numpy as np

#%% Function related to data rearrangement 

def create_compilation_tree(files_info, file_target):
    """
    INPUT: dictionary of the files (file info) and the name of the target file (file target) 
    The function create a "tree" of file that you need to compile in order to compile the target file.
    (The output is not a tree data structure but I called in this way because the data are organized with a hierarchical logic )
    """
    
    # Return variable. Each element is a list containing all the file that must be compiled for that layer
    layer_list  = [[file_target]]
    
    # Parent files for the layer that I'm analyzing in this moment
    current_layer_parent_files = []
    current_layer_parent_files += files_info[file_target]['dependencies_list']
    
    # Eventual parents of the files of the next layer (i.e. the parents of the files in current_layer_parent_files) 
    next_layer_parent_files = []
    
    # Temporary variable used to create a new layer
    tmp_layer = []
    
    # At each iteration I analyze a new file of the current layer and I save the eventual parents in next_layer_parent_files
    # When I finish the elements in current_layer_parent_files I check if the length of next_layer_parent_files
    # If length > 0 there are more parents file and I repeat everything. Otherwise I stop the cycle
    while(len(current_layer_parent_files) > 0):
        tmp_file = current_layer_parent_files.pop(0)
        
        tmp_layer.append(tmp_file)
        
        next_layer_parent_files += files_info[tmp_file]['dependencies_list']
        
        if(len(current_layer_parent_files) == 0):
            # Add the layer to the list of layers
            layer_list.append(tmp_layer)
            
            # Remove duplicates (if there are) and create new list of parents
            current_layer_parent_files = list(set(next_layer_parent_files))
            
            # Clean old lists
            next_layer_parent_files = []
            tmp_layer = []
            
    return layer_list

    
def sort_target_by_attribute(target_list, attribute = 'poinst', reverse = True):
    """
    "Sort" the key of dictionary so that when they are cycled the first one is the one with the hight attribute etc
    """
    
    return {k: v for k, v in sorted(target_list.items(), key=lambda item: item[1][attribute], reverse = reverse)}


def create_compilation_tree_per_targets(files_info, targets):
    # For each target contain its "list" of files to compile
    compilation_tree_per_target = {}

    for tmp_target in targets: 
        compilation_tree_per_target[tmp_target] = create_compilation_tree(files_info, tmp_target) 
        
    return compilation_tree_per_target

#%% 

def compute_solution(C, files_info, targets, compilation_tree_per_target):
    t = 0
    
    current_elaboration = []
    tmp_compilation_trees = []
    i = 0
    for target in targets:
        tmp_compilation_trees.append(compilation_tree_per_target[target])
    
    while(True):
        t += 1
        
        
def clean_compilation_tree(compilation_tree):
    idx_to_remove = []
    for i in range(len(compilation_tree)):
        if(len(compilation_tree[i]) == 0): idx_to_remove.append(i)
    
    idx_to_remove.append(i)
    
    for idx in idx_to_remove: del compilation_tree[i]
    
    
def choose_file_by_compilation_time(file_list, files_info):
    """
    Given a list of file return the one with the lowest compilation time and REMOVE it from the list
    """
    
    c_min = 1e9
    c_min_idx = 0
    
    for i in range(len(file_list)):
        file = file_list[i]
        if(files_info[file]['c'] < c_min):
            c_min = files_info[file]['c']
            c_min_idx = i
    
    c_min_file = file_list.pop(c_min_idx)
            
    return c_min_file

#%% Debug/Visualization function

def compute_layers_string(layer_list):
    """
    Given layer list create a string where each layer is more indented than the previous one.
    Used for debug.
    """
    
    layers_string = ""
    tabulation = ""
    for layer in layer_list:
        for file in layer:
            layers_string += tabulation + str(file) + "\n"
        tabulation += "\t"
        
    return layers_string


def show_layers(layer_list):
    print(compute_layers_string(layer_list))