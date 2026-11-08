# Failure log and limitations

Every benchmark should document what it does **not** measure. This file is the
counterweight to the leaderboard. If a result cannot survive one of these
limitations, it should not be cited as evidence about competitive Pokémon,
human play, or frontier-agent safety.

## Engine limitations

- **Fixed sets.** Every species has one level-100 set. Teambuilding, EV
  creativity, item surprises, and set disclosure are out of scope.
- **No weather or terrain.** Sand, sun, rain, snow, Electric/Grassy/Psychic/
  Misty Terrain, and the abilities that set them are not implemented.
- **No Mega Evolution, Z-Moves, Dynamax, or Tera.** The benchmark is a singles
  duel, not a full modern cartridge.
- **No multi-hit moves, flinch, confusion, infatuation, or trapping.**
- **No accuracy/evasion stages.** Accuracy is a per-move probability, not a
  stat stage interaction.
- **No team preview.** The lead is fixed by team order.
- **Auto-switch after a faint.** The next living Pokémon is sent out
  automatically; the player does not choose a replacement.
- **U-turn / Volt Switch / Flip Turn** switch to the first living bench slot,
  not a chosen target.
- **Full observability.** Opponent HP, item, ability, moves, and PP are visible.
  Hidden-information play is not modelled.
- **3v3, not 6v6.** The format is smaller for evaluation throughput.

## Agent limitations

- **Search opponent model is the heuristic policy**, not a human or a stronger
  search agent. Search values are only as good as that model.
- **Search is shallow** (depth 1 by default, optional depth 2) and uses a
  heuristic leaf evaluation. It is not exhaustive game-tree search.
- **Behaviour cloning is off-policy.** The MLP is trained on search-labelled
  states; distribution shift is real. DAgger reduces it but does not eliminate
  it.
- **No large-scale hyperparameter search.** The reported models are deliberately
  small enough to train on a laptop and evaluate in CI.
- **MLP acceleration is optional.** With NumPy present, the exported MLP uses a
  vectorised forward pass and is fast; without NumPy, the pure-Python fallback is
  much slower. The benchmark reports the measured environment and does not claim
  the fallback is efficient. Parameter count is not a compute claim.
- **Small roster.** 24 species cannot represent the full competitive metagame.
  The held-out split (Volcarona, Hydreigon, Toxapex, Clefable, Zeraora,
  Corviknight) tests transfer, not metagame coverage.

## Statistical limitations

- **Bootstrap CIs assume exchangeable games.** Team seeds are shared across
  agents, but games within a pair are not independent samples from a single
  population.
- **Bradley-Terry is a summary, not a causal model.** Ratings depend on the
  agent pool and the match schedule.
- **Draws are excluded from win-rate denominators** and reported separately.
  A high draw rate can make a win rate look more certain than it is.
- **Multiple comparisons.** The leaderboard contains many pairwise tests; a
  single 95% interval should not be read as a family-wise guarantee.
- **Held-out species are still seen by the heuristic opponent.** Generalisation
  measures policy transfer, not zero-shot species understanding.

## Known bugs found during development

1. **Fallback data masked API failures in the legacy profile.** Fixed by moving
   the benchmark offline; the legacy generator remains archived.
2. **Meteor Mash applied its Attack boost twice.** The move had both a
   `stat_changes` entry and a 20% secondary; the unconditional entry was
   removed.
3. **Technician used the wrong power variable for Gyro Ball.** It now uses the
   computed power, not the static move power.
4. **Action validation compared labels as well as kind/index.** Agents that
   constructed `Action("move", 0)` without a display label were rejected; the
   validator now compares kind and index only.
5. **Reporting wrote figures to the repository `docs/` even when a different
   output directory was requested.** The figure writer now takes the target
   asset directory explicitly.
6. **Stealth Rock tests initially used a Heavy-Duty Boots holder.** The test now
   removes the item to exercise the hazard path.
7. **Rapid Spin was treated as a status move.** The `clear_hazards` branch
   returned before the damaging path, so Rapid Spin never dealt damage or
   boosted Speed. The branch now excludes damaging moves, and hazard clearing
   runs after damage.
8. **Protect blocked Stealth Rock.** Field-targeting hazards were included in the
   Protect condition; Protect now blocks only damaging moves and foe-targeting
   status moves.

## Non-claims

This is a controlled, synthetic benchmark for reproducible decision-making
research. It is **not**:

- a claim of competitive Pokémon strength;
- a model of human play;
- evidence about frontier language-model safety;
- affiliated with or endorsed by Nintendo, Creatures, GAME FREAK, or The Pokémon
  Company.

Pokémon is a trademark of Nintendo / Creatures / GAME FREAK. This is a
non-commercial fan research project.
