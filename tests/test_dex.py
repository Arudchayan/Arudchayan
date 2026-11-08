from pokerl.dex import (
    ALL_SPECIES,
    HELD_OUT_SPECIES,
    MOVES,
    SETS,
    SPECIES,
    TRAIN_SPECIES,
    sample_team,
)
from pokerl.rng import RNG


def test_roster_and_sets_are_complete():
    assert len(SPECIES) == 24
    assert len(SETS) == len(SPECIES)
    assert set(SETS) == set(SPECIES)
    assert set(TRAIN_SPECIES).isdisjoint(HELD_OUT_SPECIES)
    assert len(TRAIN_SPECIES) + len(HELD_OUT_SPECIES) == len(ALL_SPECIES)


def test_every_set_is_legal():
    for species_id, pset in SETS.items():
        pset.validate()
        assert pset.species == species_id
        assert len(pset.moves) == 4
        assert pset.ability in SPECIES[species_id].abilities
        assert sum(pset.evs.values()) <= 508
        for move_id in pset.moves:
            assert move_id in MOVES


def test_expected_meta_values():
    assert SPECIES["garchomp"].base_stats["atk"] == 130
    assert SPECIES["blissey"].base_stats["hp"] == 255
    assert SPECIES["toxapex"].base_stats["def"] == 152
    assert SPECIES["gengar"].types == ("ghost", "poison")


def test_sample_team_is_deterministic_and_distinct():
    a = sample_team(ALL_SPECIES, 3, RNG(4))
    b = sample_team(ALL_SPECIES, 3, RNG(4))
    assert a == b
    assert len(set(a)) == 3
