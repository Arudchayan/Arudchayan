# Roadmap

PokéLab prioritizes reproducibility, explicit benchmark scope, and zero runtime
dependencies. Items below are research directions, not dated commitments.
Proposals that add scope should keep the default install dependency-free and
preserve deterministic replay.

## Next

### 6v6 and team preview

The engine already supports 3v3 with switching, hazards, and entry abilities.
The next step is 6v6 team preview, chosen leads, and a replacement policy after
a faint. This is the largest gap between the benchmark and cartridge play.

### Human baseline

Build a small local web arena where a human chooses legal actions under the same
observation and time budget. Report human-vs-agent Elo alongside agent-vs-agent
Elo. A benchmark without a human reference can still be useful, but it cannot
claim human-relevant difficulty.

### LLM agent arena

Add a JSONL protocol and optional HTTP adapter for language-model policies. The
arena should record prompts, legal-action constraints, latency, token cost, and
failures. SDKs and API clients stay in an optional extra; the core engine remains
dependency-free.

### Learned value functions

Train compact value networks on search returns and use them as leaf evaluators.
The key experiment is whether a learned value function closes the depth-2 search
gap at depth-1 cost. This is a cleaner research question than another policy
clone.

### Distillation under distribution shift

The current MLP behaviour clone is a deliberately honest negative result: it
imitates search labels but compounds errors. Next: DAgger with a stronger
expert, uncertainty-weighted labels, and a value-based objective. Report the
strength–compute frontier, including the failures.

### Adversarial and population evaluation

Add population-based training, exploitability estimates, seed-sensitivity
analysis, and targeted opponent generation. A policy that only beats the
heuristic is not evidence of robustness.

### Roster and benchmark versioning

Expand the fixed sets and the train/held-out split. Version benchmark pools so a
roster change cannot silently invalidate historical results. Preserve old result
files and document the version boundary.

## Guiding principles

- Deterministic by default: every result is reproducible from a seed and a
  command.
- Zero runtime dependencies: optional tooling belongs behind extras.
- Explicit scope: omissions are documented rather than hidden.
- Evidence over claims: reports include seeds, config hashes, sample sizes, and
  confidence intervals.
- Failures are first-class: every known bug and limitation has a home in
  [FAILURES.md](FAILURES.md).
