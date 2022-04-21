def get_file():
    """
    Read the dataset return them as a list of strings
    """
    file_list = ['a_example.in', 'b_narrow.in', 'c_urgent.in', 'd_typical.in', 'e_intriguing.in', 'f_big.in']
    data = []

    for i in range(len(file_list)):
        tmp_file = open("final_round_2019/{}".format(file_list[i]), "r")
        data.append(tmp_file.read())
        tmp_file.close()
        
    del tmp_file
    
    return data


def extract_info(file):
    """
    From the dataset string extract the relevant information for each file
    """
    
    divided_file = file.split("\n")
    
    # Extract number of file (C), number of target files (T) and number of servers (S)
    C = int(divided_file[0].split(" ")[0])
    T = int(divided_file[0].split(" ")[1])
    S = int(divided_file[0].split(" ")[2])
    
    # Extract info for each file
    file_info_dict = {}
    for i in range(1, C + 1):
        tmp_file_info = {}
        
        idx = i * 2 - 1
        file_info = divided_file[idx].split(" ")
        file_dependencies = divided_file[idx + 1].split(" ")
        
        file_name = file_info[0]
        compilation_time = int(file_info[1])
        replication_time = int(file_info[2])
        
        n_dependencies = int(file_dependencies[0])
        dependencies_list = []
        if(n_dependencies > 0):
            for j in range(n_dependencies):
                dependencies_list.append(file_dependencies[j + 1])
        
        tmp_file_info['c'] = compilation_time
        tmp_file_info['r'] = replication_time
        tmp_file_info['n_dependencies'] = n_dependencies
        tmp_file_info['dependencies_list'] = dependencies_list
        tmp_file_info['replicated'] = False
        
        file_info_dict[file_name] = tmp_file_info
    
    # Extract info about the target files
    file_target_dict = {}
    for i in range(idx + 2, idx + 2 + T):
        tmp_target_info = {}
        target_info = divided_file[i].split(" ")
        
        target_name = target_info[0]
        tmp_target_info['deadline'] = int(target_info[1])
        tmp_target_info['points'] = int(target_info[2])
        
        file_target_dict[target_name] = tmp_target_info
        
    return C, T, S, file_info_dict, file_target_dict


def clean_target(targets, files_info):
    new_targets = {}
    for file in targets:
        if(targets[file]['deadline'] > files_info[file]['c']): new_targets[file] = targets[file]
       
    return new_targets
        