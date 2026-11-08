from pokerl.types import TYPE_INDEX, TYPES, effectiveness, is_immune, stab


def test_chart_is_complete():
    assert len(TYPES) == 18
    assert len(TYPE_INDEX) == 18
    assert set(TYPE_INDEX) == set(TYPES)


def test_known_effectiveness():
    assert effectiveness("electric", ["water", "flying"]) == 4.0
    assert effectiveness("ground", ["flying"]) == 0.0
    assert effectiveness("fighting", ["ghost"]) == 0.0
    assert effectiveness("fire", ["grass", "steel"]) == 4.0
    assert effectiveness("water", ["fire"]) == 2.0
    assert effectiveness("normal", ["rock"]) == 0.5


def test_immunity_helper():
    assert is_immune("electric", ["ground"])
    assert not is_immune("electric", ["water"])


def test_stab():
    assert stab("dragon", ["dragon", "ground"]) == 1.5
    assert stab("fire", ["dragon", "ground"]) == 1.0
