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
    
        self.update_adjacency_matrix()
    
    def update_adjacency_matrix(self, use_dense_matrix = False):
        self.adj_mat = nx.adjacency_matrix(self.G)
        if(use_dense_matrix): self.adj_mat = self.adj_mat.todense()
        
    
    def remove_file(self, file):
        self.G.remove_node(file)
        
    def draw(self, figsize = (20, 10)):
        color_map = []
        for node in self.G: 
            # print(node, self.files_info[node]['n_dependencies'])
            if(self.files_info[node]['n_dependencies'] == 0): color_map.append('blue')
            else:  color_map.append('green')
            
        plt.figure(figsize = figsize)
        nx.draw(self.G, with_labels = True, node_color = color_map)
        
        