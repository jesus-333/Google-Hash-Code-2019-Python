from solchecker import loadInstance, loadSolution, evalCheck

solution_file_list = ['solution_b_narrow_1.txt', 'solution_c_urgent_1.txt', 'solution_d_typical_1.txt', 'solution_f_big_1.txt']
total_score = 0

for solution_file in solution_file_list:
    file_name = solution_file[9:-6] + ".in"

    instance = loadInstance("final_round_2019/{}".format(file_name))
    solution = loadSolution("solution/" + solution_file, instance)
    
    tmp_score = evalCheck(instance, solution)
    total_score += tmp_score
    
    print("Score =", tmp_score, "\t", file_name)
    
    
# Add the results for file a and e
print("Total score: ", total_score + 60 + 1)
