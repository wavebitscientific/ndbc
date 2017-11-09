# ndbc

[![Build Status](https://travis-ci.org/wavebitscientific/ndbc.svg?branch=master)](https://travis-ci.org/wavebitscientific/ndbc)
[![GitHub issues](https://img.shields.io/github/issues/wavebitscientific/ndbc.svg)](https://github.com/wavebitscientific/ndbc/issues)

A Python interface to National Data Buoy Center data.

## Getting started

```
pip install git+https://github.com/wavebitscientific/ndbc
```

## Usage

```python
from ndbc import Station
from datetime import datetime

# initialize without getting the data
station = Station(42001)

station.name
# 'MID GULF - 180 nm South of Southwest Pass, LA'

station.lon
# -89.668

station.lat
# 25.897

# initialize and get the data
station = Station(42001, datetime(2017,10,1), datetime(2017,11,1))

# get a different time window
station.get_stdmet(datetime(2015,1,1), datetime(2017,1,1))

```

## Features

* [x] Standard meteorological data: wind speed and direction, air pressure, air and water temperature, dew-point temperature, wave height, period, and direction.
* [ ] Omnidirectional (1-d) wave spectrum data
* [ ] Directional (2-d) wave spectrum data
* [ ] Derived diagnostics
* [ ] [What else?](https://github.com/wavebitscientific/ndbc/issues/new)
