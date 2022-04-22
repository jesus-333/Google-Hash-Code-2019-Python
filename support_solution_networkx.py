import numpy as np

import networkx as nx

import matplotlib.pyplot as plt

#%%

class compilationTreeNX():
    
    def __init__(self, target, compilation_tree_list, files_info):
        """
        Class that create REAL compilation tree for each file using the networkx library. 
        It need the name of the target, the compilation list for the target and the dictionary with all the files info
        """
        
        # Create directed graph
        self.G = nx.DiGraph()
        
        self.files_info = files_info
        
        # Insert node (file) in the graph
        for layer in compilation_tree_list: 
            for file in layer:
                self.G.add_node(file)
        
        
        # Insert edges (dependencies) in the graph.
        # N.B. I Have to to two separate cycle because I have to insert all the nodes before create the link
        for layer in compilation_tree_list: 
            for file in layer:
                for dependency in files_info[file]['dependencies_list']:
                    self.G.add_edge(dependency, file)
    
        # Create adjancey matrix and leaf list
        self.update_adjacency_matrix()
        self.update_leaf()
    
    
    def update_adjacency_matrix(self, use_dense_matrix = False):
        self.adj_mat = nx.adjacency_matrix(self.G)
        if(use_dense_matrix): self.adj_mat = self.adj_mat.todense()
                
    
    def update_leaf(self, update_adj_mat = True):
        tmp_node_list = list(self.G.nodes())
        
        if(update_adj_mat): self.update_adjacency_matrix(True)
        n_dependencies_per_node = np.asarray(np.sum(self.adj_mat, 0))[0]
        
        self.leaf_list = []
        for i in range(len(n_dependencies_per_node)):
            if(n_dependencies_per_node[i] == 0): self.leaf_list.append(tmp_node_list[i])
    
    
    def remove_file(self, file):
        # Remove the node
        self.G.remove_node(file)
        
        # Update adjancey matrix and leafs list
        if(len(self.G.nodes()) > 0):
            self.update_adjacency_matrix()
            self.update_leaf()
        else:
            self.leaf_list = []
            self.adj_mat = None
        
                
    def draw(self, figsize = (20, 10)):
        color_map = []
        for node in self.G: 
            # print(node, self.files_info[node]['n_dependencies'])
            if(self.files_info[node]['n_dependencies'] == 0): color_map.append('blue')
            else:  color_map.append('green')
            
        plt.figure(figsize = figsize)
        nx.draw(self.G, with_labels = True, node_color = color_map)
        
#%%

def clean_solution(solution_string, file_name, idx_server):
    """
    Remove the line containing the specific file name and idx_server from the solution
    """
    
    new_solution_string = ""
    
    for line in solution_string.split("\n"):
        if(len(line) > 0):
            line_file = line.split(" ")[0]
            line_server = int(line.split(" ")[1])
            
            # print(line_file, file_name, line_file != file_name)
            # print(line_server, idx_server, line_server != idx_server)
            if(line_file != file_name or line_server != idx_server): new_solution_string += line + "\n"
        
    return new_solution_string


def clean_dependency(dep_file, files_info):
    """
    Remove the dep_file from the depency of all the files inside the dictionary
    """
    
    for file in files_info:
        if dep_file in files_info[file]['dependencies_list']:
            files_info[file]['dependencies_list'].remove(dep_file)
            files_info[file]['n_dependencies'] -= 1