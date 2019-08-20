# Development

## Install

To run test and build tasks, install [`nox`][1]:

```
python3 -m pip install --upgrade 'nox >= 2019.8.20'
```

## Unit Tests

```
nox -s unit-3.7 -r
# OR
python3 -m nox -s unit-3.7 -r
```

[1]: https://nox.thea.codes
