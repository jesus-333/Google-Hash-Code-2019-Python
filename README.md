# Google Hash Code 2019 Python
 Solution to the google hash code 2019 in Python. The total score is 3570614 divided as in the table below.


|       File      |  Score  |
|:---------------:|:-------:|
|   a_example.in  |    60   |
|   b_narrow.in   | 1346790 |
|   c_urgent.in   | 1312825 |
|   d_typical.in  |  69967  |
| e_intriguing.in |    1    |
|     f_big.in    |  840971 |

The solution is based on tree data structure. For each target I create a tree of dependencies. Then each target is assigned to a server (so each server is dedicated to a specific target). The file compiled are the leaf of the tree (i.e. the file without dependencies). When a file is compiled the relative leaf is removed from the compilation tree. When a file is replicated it is removed from all the compilation tree. If there are more server than target the extra server are assigned to compiled random file (alternatively you can choose to compile the file with the highest compilation time between all the file in all the compilation tree that is currently nor compiling or replicating)

## Requirements
The solver 3 (the final one) require the [networkx](https://networkx.org/) package and the [scipy](https://scipy.org/) package to work.
If you have any problem install them with conda 
```python
conda install -c anaconda scipy

conda install -c anaconda networkx 
```

## Notes
The solver is still (somehow) bugged and sometimes with file *d_typical* has caused problem with dependencies. For the other files I don't have seen this any error (for now).
The creation time of the solution is quite big for file b and c.

For  more info write me an email.
