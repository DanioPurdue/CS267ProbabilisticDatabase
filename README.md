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
