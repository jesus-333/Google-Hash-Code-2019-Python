import numpy as np

def create_compilation_tree(file_info, file_target):
    """
    INPUT: dictionary of the files (file info) and the name of the target file (file target) 
    The function create a "tree" of file that you need to compile in order to compile the target file.
    (The output is not a tree data structure but I called in this way because the data are organized with a hierarchical logic )
    """
    
    # Return variable. Each element is a list containing all the file that must be compiled for that layer
    layer_list  = [[file_target]]
    
    # Parent files for the layer that I'm analyzing in this moment
    current_layer_parent_files = file_info[file_target]['dependencies_list']
    
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