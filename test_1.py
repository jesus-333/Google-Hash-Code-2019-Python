import numpy as np

from support_data_extraction import get_file, extract_info

#%%

data = get_file()

C, T, S, file_info, targets =  extract_info(data[1])