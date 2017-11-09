from . import Station

def test_ndbc_station():
    assert type(Station(42002)) is Station
