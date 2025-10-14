# Welcome to OpenJij's documentation!


## OpenJij : Ising model と QUBOのためのヒューリスティクスソルバー

[![PyPI version shields.io](https://img.shields.io/pypi/v/openjij.svg)](https://pypi.python.org/pypi/openjij/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/openjij.svg)](https://pypi.python.org/pypi/openjij/)
[![PyPI implementation](https://img.shields.io/pypi/implementation/openjij.svg)](https://pypi.python.org/pypi/openjij/)
[![PyPI format](https://img.shields.io/pypi/format/openjij.svg)](https://pypi.python.org/pypi/openjij/)
[![PyPI license](https://img.shields.io/pypi/l/openjij.svg)](https://pypi.python.org/pypi/openjij/)
[![PyPI download month](https://img.shields.io/pypi/dm/openjij.svg)](https://pypi.python.org/pypi/openjij/)
[![Downloads](https://pepy.tech/badge/openjij)](https://pepy.tech/project/openjij)


# Introduction

[Github repository](https://github.com/Jij-Inc/OpenJij)
[OpenJij Website](https://www.openjij.org/)

This project is still going. If you can help, please join in the OpenJij Slack Community. Then, you can participate in the project, and ask questions.

[OpenJij Discord Community](https://discord.gg/Km5dKF9JjG)

## What is OpenJij ?


OpenJij is a heuristic optimization library of the Ising model and QUBO.
It has a Python interface, therefore it can be easily written in Python, although the core part of the optimization is implemented with C++.
Let's install OpenJij.

# Install

## pip

```shell
$ pip install openjij
```

# Minimum sample code

## Simulated annealing (SA)

### for the Ising model

to get a sample that executed SA 100 times
```python
import openjij as oj
n = 10
h, J = {}, {}
for i in range(n-1):
    for j in range(i+1, n):
        J[i, j] = -1
sampler = oj.SASampler()
response = sampler.sample_ising(h, J, num_reads=100)
# minimum energy state
print(response.first.sample)
# {0: -1, 1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1}
# or
# {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
# indices (labels) of state (spins)
print(response.indices)
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

# Parameters customize

## Customize annealing schedule


```python
import openjij as oj
n = 10
h, J = {}, {}
for i in range(n-1):
    for j in range(i+1, n):
        J[i, j] = -1
# customized annealing schedule
# list of [beta, monte carlo steps in beta]
schedule = [
    [10, 3],
    [ 5, 5],
    [0.5, 10]
]
sampler = oj.SASampler()
response = sampler.sample_ising(h, J, schedule=schedule)
print(response)
```

# Higher order model  

If you want to handle higher order model as follows:    
```{math}
H = \sum_{i}h_i\sigma_i + \sum_{i < j} J_{ij} \sigma_i \sigma_j + \sum_{i, j, k} K_{i,j,k} \sigma_i\sigma_j \sigma_k \cdots \\
``` 

use `.sample_hubo`

> HUBO: Higher order unconstraint binary optimization
## Sample code
```python
import openjij as oj
# Only SASampler can handle HUBO.
sampler = oj.SASampler()
# make HUBO
J = {(0,): -1, (0,1): -1, (0,1,2): 1}
response = sampler.sample_hubo(J, vartype="SPIN")
print(response)
#    0  1  2 energy num_oc.
# 0 +1 +1 -1   -3.0       1
# ['SPIN', 1 rows, 1 samples, 3 variables]
response = sampler.sample_hubo(J, vartype="BINARY")
print(response)
#    0  1  2 energy num_oc.
# 0  1  1  0   -2.0       1
# ['BINARY', 1 rows, 1 samples, 3 variables]
```

--------------------------------------------

# Outline

```{tableofcontents}
```
