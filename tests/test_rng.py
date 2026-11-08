from pokerl.rng import RNG


def test_same_seed_is_deterministic():
    a = RNG(123)
    b = RNG(123)
    assert [a.next_u64() for _ in range(20)] == [b.next_u64() for _ in range(20)]


def test_clone_preserves_stream():
    a = RNG(9)
    a.next_u64()
    b = a.clone()
    assert [a.random() for _ in range(10)] == [b.random() for _ in range(10)]


def test_random_is_unit_interval():
    rng = RNG(1)
    values = [rng.random() for _ in range(5000)]
    assert all(0.0 <= v < 1.0 for v in values)
    assert 0.45 < sum(values) / len(values) < 0.55


def test_randint_inclusive():
    rng = RNG(2)
    values = {rng.randint(3, 7) for _ in range(2000)}
    assert values == {3, 4, 5, 6, 7}


def test_shuffle_is_deterministic():
    a = list(range(10))
    b = list(range(10))
    RNG(5).shuffle(a)
    RNG(5).shuffle(b)
    assert a == b
    assert sorted(a) == list(range(10))
