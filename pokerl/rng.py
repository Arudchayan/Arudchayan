"""Deterministic RNG used by the simulator.

We deliberately avoid :mod:`random` for anything that can influence a battle.
Python's Mersenne Twister stream is stable in practice, but SplitMix64 gives us
an explicit, tiny, platform-independent stream that is trivial to clone for
search and replay.  The implementation is the standard SplitMix64 mixer.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

MASK64 = (1 << 64) - 1
GOLDEN_GAMMA = 0x9E3779B97F4A7C15

T = TypeVar("T")


class RNG:
    """A small, cloneable SplitMix64 random number generator."""

    __slots__ = ("state",)

    def __init__(self, seed: int = 0) -> None:
        self.state = seed & MASK64

    def clone(self) -> RNG:
        other = RNG(0)
        other.state = self.state
        return other

    def next_u64(self) -> int:
        self.state = (self.state + GOLDEN_GAMMA) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return (z ^ (z >> 31)) & MASK64

    def random(self) -> float:
        """Uniform float in [0, 1)."""
        return (self.next_u64() >> 11) * (1.0 / (1 << 53))

    def randint(self, a: int, b: int) -> int:
        """Inclusive integer in [a, b]."""
        if b < a:
            raise ValueError("b must be >= a")
        return a + self.next_u64() % (b - a + 1)

    def chance(self, probability: float) -> bool:
        return self.random() < probability

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.random()

    def choice(self, seq: Sequence[T]) -> T:
        if not seq:
            raise IndexError("cannot choose from an empty sequence")
        return seq[self.next_u64() % len(seq)]

    def shuffle(self, seq: list[T]) -> None:
        for i in range(len(seq) - 1, 0, -1):
            j = self.next_u64() % (i + 1)
            seq[i], seq[j] = seq[j], seq[i]
