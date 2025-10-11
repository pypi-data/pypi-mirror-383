# GeneticPy

[![codecov](https://codecov.io/gh/geneticpy/geneticpy/branch/master/graph/badge.svg)](https://codecov.io/gh/geneticpy/geneticpy)
[![PyPI version](https://badge.fury.io/py/geneticpy.svg)](https://badge.fury.io/py/geneticpy)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/geneticpy.svg)](https://pypi.python.org/pypi/geneticpy/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/geneticpy?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/geneticpy)

GeneticPy is an optimizer that uses a genetic algorithm to quickly search through custom parameter spaces for optimal solutions.

### Installation

GeneticPy requires Python 3.10+

```sh
pip install geneticpy
```

### Development Workflow

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management and [hatchling](https://github.com/pypa/hatch) as the build backend.

```sh
# Run tests
make test

# Build the package
make build
```

### Optimize Example:

A brief example to get you started is included below:

```python
import geneticpy

def loss_function(params):
  if params['type'] == 'add':
    return params['x'] + params['y']
  elif params['type'] == 'multiply':
    return params['x'] * params['y']

param_space = {'type': geneticpy.ChoiceDistribution(choice_list=['add', 'multiply']),
               'x': geneticpy.UniformDistribution(low=5, high=10, q=1),
               'y': geneticpy.GaussianDistribution(mean=0, standard_deviation=1)}

results = geneticpy.optimize(loss_function, param_space, size=200, generation_count=500, verbose=True)
best_params = results.best_params
loss = results.best_score
total_time = results.total_time
```

### PyPi Project
https://pypi.org/project/geneticpy/

### Contact

Please feel free to email me at brandonschabell@gmail.com with any questions or feedback.
