import numpy as np

#%% Function related to data rearrangement (SOLUTION 1)

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

#%% Function related to data rearrangement (SOLUTION 1)

class compilationTree():
    
    def __init__(self, target, files_info):
        """
        Class that create REAL compilation tree for each file. 
        It need the name of the target and the dictionary with all the files info
        """
        self.root = fileNode(target, files_info)
        
        self.tree_leafs = list(set(self.__get_leaf([], self.root)))
        
    def get_leaf(self, update = False):
        if(update): self.update_leaf()
        return self.tree_leafs
        
    def __get_leaf(self, leaf_list, node):
        if(len(node.leaf) == 0): 
            tmp_list = leaf_list + [node]
            # print(node.name)
            # print(tmp_list)
            return tmp_list
        else:
            for child_node in node.leaf: leaf_list += self.__get_leaf(leaf_list, child_node)
            
            return leaf_list      
        
    def update_leaf(self): self.tree_leafs = list(set(self.__get_leaf([], self.root)))
    
    
    def remove_leaf(self, leaf_name):
        return self.__remove_leaf(leaf_name, self.root)
            
    def __remove_leaf(self, name, node):
        idx_to_remove = -1
        for i in range(len(node.leaf)):
            leaf = node.leaf[i]
            if(leaf.name == name): 
                idx_to_remove = i
                
            else: self.__remove_leaf(name, leaf)
        
        if(idx_to_remove == -1): 
            return 0
        else:
            del node.leaf[idx_to_remove]
            self.update_leaf()
            return 1
        
    
class fileNode():
    def __init__(self, file_name, files_info):
        self.name = file_name
        self.c = files_info[file_name]['c']
        self.r = files_info[file_name]['r']
        
        self.replicated = False
        
        self.leaf = []
        for dependency in files_info[file_name]['dependencies_list']: 
            if(dependency == self.name): raise Exception("LOOP")
            self.leaf.append(fileNode(dependency, files_info))
        
        self.leaf_dict = {}
        for dependency in files_info[file_name]['dependencies_list']: self.leaf_dict[dependency] = fileNode(dependency, files_info)
        
        self.leaf_name = files_info[file_name]['dependencies_list']
        
    def __getitem__(self, idx):
        return self.leaf[idx], self.leaf_name[idx]
    
    def __repr__(self):
        tmp_string = ""
        tmp_string += "Leaf name: {}\n".format(self.name)
        tmp_string += "\tc = {}\tr = {}".format(self.c, self.r)
        
        return tmp_string
    
    
class shallowNode():
    def __init__(self, file_name, files_info):
        self.name = file_name
        
        self.leaf = []
        for dependency in files_info[file_name]['dependencies_list']: self.leaf.append(shallowNode(dependency, files_info))
        
        self.leaf_name = files_info[file_name]['dependencies_list']
        
    def __getitem__(self, idx):
        return self.leaf[idx], self.leaf_name[idx]
    
    def __repr__(self):
        tmp_string = ""
        tmp_string += "Leaf name: {}\n".format(self.name)
        
        return tmp_string
    
#%% 


def clean_compilation_tree(compilation_tree):
    idx_to_remove = []
    for i in range(len(compilation_tree)):
        if(len(compilation_tree[i]) == 0): idx_to_remove.append(i)
    
    # Start from the greats index
    idx_to_remove.reverse()
    
    # Remove compilation tree
    for idx in idx_to_remove: del compilation_tree[i]
    
    
def choose_file_by_compilation_time(file_list, files_info, remove_file_from_list = True):
    """
    Given a list of file return the one with the lowest compilation time. 
    If remove_file_from_list is set to True it REMOVE the file from the list
    """
    
    c_min = 1e9
    c_min_idx = 0
    
    for i in range(len(file_list)):
        file = file_list[i]
        if(files_info[file]['c'] < c_min):
            c_min = files_info[file]['c']
            c_min_idx = i
    
    if(remove_file_from_list):
        c_min_file = file_list.pop(c_min_idx)
    else:
        c_min_file[c_min_idx]
            
    return c_min_file


def remove_file_from_dependecies_list(file_to_remove, files_info):
    """
    Given the files info dictionary the function remove the given file from the dependencies of all the file.
    Used when a file is replicated
    """
    
    for file in files_info:
        if(file_to_remove in files_info[file]['dependencies_list']): 
            files_info[file]['dependencies_list'].remove(file_to_remove)
            

def check_compilation_trees(compilation_tree_list):
    """
    Function that return True only if all the compilation tree are empty
    """
    
    for compilation_tree in compilation_tree_list:
        if(len(compilation_tree) > 0): return False
    
    return True
        

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