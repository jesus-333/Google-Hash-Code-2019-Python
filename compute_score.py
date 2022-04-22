from solchecker import loadInstance, loadSolution, evalCheck

solution_file_list = ['solution_b_narrow_1.txt', 'solution_c_urgent_1.txt', 'solution_d_typical_1.txt', 'solution_f_big_1.txt']

for solution_file in solution_file_list:
    file_name = solution_file[9:-6] + ".in"

    instance = loadInstance("final_round_2019/{}".format(file_name))
    solution = loadSolution("solution/" + solution_file, instance)
    print("Score =", evalCheck(instance, solution), "\t", file_name)
