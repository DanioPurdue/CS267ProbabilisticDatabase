# CS267A Probabilistic Database Project
## `main.py`
`main.py` controls the overall logic of the program. The extension is also invoked in the main.py program.

### Files needed for Running `main.py`

1. query file
2. table files
3. `Predicate.py`
4. `Variable.py`
5. `GibbsSampling.py`
6. `Lift.py`

## Dependencies

1. pandas
2. numpy
3. matplotlib
4. progressbar

These dependencies are in the `requiremens.txt` file.

To install them, please run

`pip install -r requirements.txt`


## Sample Command for running main.py
`Python main.py --table t2.txt --query query.txt --table t1.txt --table t3.txt --table t4.txt`

## Generating Random Data for Testing

File: `DataGenerator.py`

How to specify the number of tuples you want:

n is not the exact number of tuples in the database. **The number of tuples is on the order of  $n^2$ .**

change the n value at line 51 to ajust 

```python
if __name__ == "__main__":
    n = 100 #<--------change this n value
    print("Generate data points of size: " + str(n))
    DataGenerator(n) 
```

P, Q and R tables and they are similar to the input given in the examples **P(x), Q(x), R(x, y) and T(x,y)**

#### Tables Generated

```
test_table1.txt
test_table2.txt
test_table3.txt
test_table4.txt
```

## Extension

The implementation of the gibbs sampling extension is located in the `GibbsSampling.py` file. This file is called in the main.py program. You can change the number of steps,`num_step`, for each sampling process in the main.py program. If `num_step` is large, approximation result is closed to the real value, but it might take longer time compute.

