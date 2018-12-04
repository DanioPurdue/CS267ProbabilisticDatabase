# CS267A Probabilistic Database Project
Course Project

## `main.py`
### Files needed for running the commands
1. query file
2. table files
3. `Predicate.py`
4. `Variable.py`

### Notes
There are two variable classes: `randomVar` and `Variable`.
`randomVar` is for Gibbs sampling. @Liqi: you may change this part to suit for the gibbs sampling.
`Variable` is used in liftable inference algorithm. Please do not change it.


## Sample command for running main.py
`Python main.py --table t2.txt --query query.txt --table t1.txt`

## Generate test random data for testing

file: `DataGenerator.py`

How to specify the number of tuples you want:

change the n value at line 43

```python
if __name__ == "__main__":
    n = 100 #<--------change this n value
    print("Generate data points of size: " + str(n))
    DataGenerator(n)
```

P, Q and R tables and they are similar to the input given in the examples **P(x), Q(x), R(x, y)**

### Tables generated

```
test_table1.txt
test_table2.txt
test_table3.txt
```

