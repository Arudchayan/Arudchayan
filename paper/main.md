# PokéLab: A Deterministic, Dependency-Free Benchmark for Decision Making Under Uncertainty

*Reference draft. Empirical tables are generated from `results/*.json` by `python -m pokerl report`; table entries are not hand-typed.*

## Abstract

PokéLab is a deterministic, zero-third-party-dependency simulator and evaluation protocol for turn-based decision making under uncertainty. It implements level-100 singles with a 24-species roster, fixed sets, 18-type interactions, a documented mechanics subset, and a cloneable SplitMix64 stream. An 188-dimensional action-conditional feature map supports the learned policies; the suite spans eleven agents: random, greedy, heuristic, Search-1/2, linear and MLP behaviour cloning, DAgger, REINFORCE, Hybrid-1, and tabular Q. The protocol uses side-swapped matches on a common team schedule, percentile bootstrap intervals, Bradley-Terry ratings, and a six-species held-out split. The reference protocol and limitations are reported below.

> **Non-claims.** PokéLab is not a cartridge-accurate Pokémon simulator, a teambuilding benchmark, evidence of superhuman or general capability, or a deployment system. Version 1 is fully observable and fixed-set; results do not transfer automatically to hidden-information, 6v6, or doubles play.

## 1. Introduction

Evaluation infrastructure is a research contribution. Roster, reward, opponent, and reporting choices determine what a benchmark can show. A faithful simulator is costly to specify; a toy one does not discriminate. A useful benchmark sits between: documented mechanics, reproducible stochasticity, agents strong enough to separate, and measurement uncertainty that is visible.

Pokémon offers four useful properties: **partial observability** of teams and sets; **stochasticity** in accuracy, crits, damage rolls, sleep, and speed ties; **type-based compositional structure and generalization** across 18 attacking and defensive types; and **long-horizon resource management** of HP, PP, items, hazards, boosts, status, and the bench. Version 1 deliberately implements a full-information, fixed-set slice. It isolates stochastic and strategic uncertainty—about outcomes and opponent policy—rather than informational uncertainty, and is therefore an upper bound on hidden-information performance.

We contribute (i) a pure-Python singles engine with a documented action space, SplitMix64 stream, and explicit terminal rules; (ii) a fixed 24-species roster and a six-species held-out split; (iii) a shared 188-dimensional action-conditional feature map; (iv) eleven reference agents spanning search, imitation, RL, and tabular learning; and (v) a protocol with side-swapping, a common team schedule, bootstrap intervals, Bradley-Terry ratings, compute accounting, and falsification criteria. We do not claim any agent is strong or that rankings transfer beyond PokéLab.

## 2. Related Work

**RL environments.** Gymnasium established a common vocabulary for observations, actions, rewards, and termination; PettingZoo extends it to multi-agent settings. PokéLab borrows that vocabulary but is not a wrapper: `Battle.step` returns per-side views, rewards, and a done flag, with no such dependency. Self-containment aids auditability.

**Pokémon simulators.** Pokémon Showdown is the reference simulator for cartridge fidelity; `poke-env` provides a Python RL interface. PokéLab is not a replacement: it fixes a small roster and a documented mechanics subset, trading fidelity for control over variance and cost. A reader who needs full mechanics should use Showdown.

**RL benchmarks.** The Arcade Learning Environment made pixel control a standard test; Procgen measures generalization to generated levels; Melting Pot studies generalization to unseen co-players. PokéLab is turn-based, full-state, and two-player zero-sum. Its held-out-species split is closest to Procgen's held-out levels: a controlled input-distribution shift over species and type combinations.

**Evaluation science and LLM agents.** Reproducibility, single-seed comparisons, and unreported variance can reverse deep-RL conclusions. PokéLab responds with shared schedules, side-swapped games, intervals, all-pairs ratings, and compute reporting; Section 7 lists gaps. Agent benchmarks such as AgentBench, WebArena, SWE-bench, and GAIA evaluate language-model agents; PokéLab is not an LLM benchmark in v1, exposes numeric features, and reports no LLM results.

*No formal bibliography in this draft.*

## 3. Environment

### 3.1 State, scope, and actions

State contains both teams (species, HP, status, stages, PP, item, ability, choice lock, active), side hazards, turn, and the battle RNG. The benchmark is **1v1 and 3v3 singles** (the engine accepts six). Level is 100, IVs are 31, and each species has one fixed set; there is no team preview or teambuilding. A transition is \(T(s,a_0,a_1;\xi)\), with \(\xi\) the battle RNG. Rewards are terminal and zero-sum: \(+1\) win, \(-1\) loss, \(0\) draw.

An action is \((\text{kind},\text{index})\): up to four moves with PP, up to two switches in 3v3, a forced switch after a faint, and Struggle when no move or switch is legal. Choice items lock the user to one move. The legal set is explicit; illegal actions are hard errors.

### 3.2 Roster and fixed sets

The roster is Garchomp, Dragonite, Metagross, Gengar, Alakazam, Blissey, Skarmory, Gliscor, Heatran, Rotom-Wash, Ferrothorn, Scizor, Mamoswine, Volcarona, Hydreigon, Toxapex, Clefable, Excadrill, Gastrodon, Breloom, Zeraora, Slowbro, Landorus-Therian, and Corviknight. Their sets are fixed in `pokerl/dex.py`; declared abilities are not all active. The roster covers 17 of 18 types; no species is Rock-type. Dark and Fairy appear only on held-out species (Hydreigon, Clefable).

### 3.3 Mechanics implemented and omitted

The damage formula is

$$
D=\max\!\left(1,\left\lfloor\left(\frac{(2L/5+2)P\,A/D_{\text{def}}}{50}+2\right)\text{STAB}\cdot\text{Type}\cdot\text{Crit}\cdot\text{Item}\cdot\text{Ability}\cdot U\right\rfloor\right),
$$

with \(U\sim\mathrm{Uniform}(0.85,1.0)\), STAB \(1.5\), crits \(1/24\) at \(1.5\times\); stat stages use the standard multiplier clamped to \([-6,6]\). The engine implements accuracy checks, the 18-type chart, crits, damage rolls, burn/poison/toxic/paralysis/sleep, Leftovers, Life Orb, Choice Band/Specs/Scarf, Focus Sash, Heavy-Duty Boots, Toxic Orb, Stealth Rock, Defog, Rapid Spin, U-turn, Volt Switch, and a partial ability set including Intimidate, Multiscale, Thick Fat, Solid Rock, Sturdy, Clear Body, Mold Breaker, Technician, Magic Guard, Regenerator, Natural Cure, Poison Heal, Rough Skin/Iron Barbs, Flame Body, Levitate, Flash Fire, Storm Drain, Volt Absorb, Sweet Veil, and Water Veil. Pressure, Unaware, Merciless, Serene Grace, and Sand Rush are declared on some sets but have no mechanical effect in v1.

| Omitted or simplified | Consequence |
|---|---|
| Field and generation mechanics | No weather, terrain, screens, multi-hit, Mega, Z-moves, Dynamax, or Terastallization. |
| Extra items and abilities | No Assault Vest, Rocky Helmet, berries, or Trick; several declared abilities are inert (above). |
| Other moves and hazards | One Stealth Rock layer; no Spikes/Toxic Spikes/Web; no confusion, flinch, Taunt, Encore, Substitute, or Leech Seed. |
| Team and pivot | No preview or teambuilding; U-turn/Volt Switch sends in the lowest-index living bench Pokémon. |

### 3.4 Deterministic RNG and episode limits

All battle randomness uses SplitMix64: golden gamma, two xor-shift-multiply rounds, final xor-shift. `random()` uses the top 53 bits, and `clone()` copies the state. The battle owns one stream; each agent gets its own (`seed ^ 0xAA55`, `seed ^ 0x55AA`), so exploration does not perturb battle rolls. Search clones battle and RNG. Determinism holds for the same CPython build and float environment; damage uses floats and `int`, and `math.exp` can differ across libm implementations.

`MAX_TURNS = 100`; a battle ends when one side is empty, both are empty, or the limit is reached. At the limit, the larger team HP fraction \(\sum_i\mathrm{HP}_i/\sum_i\mathrm{maxHP}_i\) wins; an exact tie is a draw. The evaluator adds a defensive 300-decision cap (draw if hit). Draws are winner \(-1\), reward \(0\); they are excluded from win rate and half-weighted in Bradley-Terry.

### 3.5 Observation vector

`BattleView` exposes both sides' full team, moves, PP, items, and abilities. Learning uses \(\phi(s,a)\in\mathbb{R}^{188}\): 51 action, 120 global, and 17 interaction features. The action block covers identity, type, category, power/accuracy/priority, contact/recoil/drain, fixed damage, healing, setup, hazards, Protect, pivot, STAB/effectiveness, expected damage, can-KO, boosts, status chance, PP, and six switch features. The global block covers HP/alive, speed, boosts, statuses, hazards, turn, bench HP, type advantage, Choice/Regenerator/Levitate, type one-hots, stats, item/ability flags, and threats. Interactions are selected products. The map is shared and unstandardized (Appendix A); Tabular Q uses a separate key.

## 4. Agents

The suite contains Random, Greedy, Heuristic, Search-1/2, Linear BC, MLP BC, DAgger, REINFORCE, Hybrid-1, and Tabular Q.

**Random, greedy, heuristic.** Random samples uniformly from the legal set. Greedy maximizes estimated damage fraction times accuracy; switches and status moves score zero, and ties go to the first action. Heuristic scores each action with fixed terms for expected damage, KO, priority, contact/recoil, secondary status, Knock Off, healing, Protect, hazards, setup, and switching; search uses a positional value \(V_h\) combining team HP, alive count, boosts, bench HP, matchup quality, status, hazards, and Regenerator.

**Search.** Search-\(d\) is expectimax with a heuristic opponent model. Let \(\mathcal O_k(s)\) be the opponent's top-\(k\) actions under the heuristic score and

$$
\pi_\beta(o\mid s)=\frac{\exp(h(s,o)/\beta)}{\sum_{o'\in\mathcal O_k(s)}\exp(h(s,o')/\beta)}
$$

a softmax model with \(\beta=18\), \(k=6\) (the reference CLI uses \(k=3\)). Then

$$
Q_d(s,a)=\sum_{o\in\mathcal O_k(s)}\pi_\beta(o\mid s)\,V_{d-1}\big(T(s,a,o;\xi)\big),\qquad V_0(s)=V_h(s),
$$

where \(\xi\) is the cloned RNG stream. The expectation is over the opponent's policy, not over all stochastic transitions: each branch samples one transition realization. \(d\) counts decision rounds: depth 1 evaluates after one action per side; depth 2 expands one more round. With up to six legal actions in 3v3 and \(k=6\), depth 1 expands at most \(6\times6=36\) children and depth 2 at most \(6\times6\times6\times6=1{,}296\).

**Behaviour cloning and DAgger.** The linear policy is

$$
\pi_\theta(a\mid s)=\frac{\exp(\theta^\top\phi(s,a))}{\sum_{a'\in\mathcal A(s)}\exp(\theta^\top\phi(s,a'))}.
$$

Targets are soft search distributions \(q_i(a)\propto\exp(Q_1(s_i,a)/\tau)\) with \(\tau=0.1\); training minimizes \(-\frac1N\sum_i\sum_a q_i(a)\log\pi_\theta(a\mid s_i)+\lambda\|\theta\|^2\). The linear model uses online SGD (lr 0.05, decay 0.985/epoch, \(\lambda=10^{-4}\)), a 12% validation split, and best-validation checkpointing. The MLP replaces the linear logit with a shared two-hidden-layer ReLU trunk (64, 32), trained with AdamW and early stopping; PyTorch is optional and inference uses a JSON export. DAgger aggregates states visited by the current policy \(\pi_k\), labels them with search, and retrains:

$$
\mathcal D_{k+1}=\mathcal D_k\cup\{(s,\pi^*(s)):s\sim d_{\pi_k}\}.
$$

The reference MLP DAgger uses two iterations of 600 decisions and 100 evaluation games against the heuristic; the linear helper defaults to three iterations of 400 and 80. The ceiling is the search teacher, not an optimal policy.

**REINFORCE and tabular Q.** REINFORCE fine-tunes the BC policy with

$$
\nabla_\theta J(\theta)=\mathbb E_{\tau\sim\pi_\theta}\left[\frac1T\sum_{t=1}^T\nabla_\theta\log\pi_\theta(a_t\mid s_t)(R(\tau)-b)\right],
$$

using \(b\leftarrow0.95b+0.05R\), 2,000 episodes, lr 0.02, and evaluation every 250 episodes on 80 games. It is undiscounted and episode-level: the same terminal advantage weights every decision, and the stored `gamma` is not applied to per-step returns. Tabular Q uses a discretized state (species, six HP bins, status, boosts, hazards, bench HP bins, turn decade) and ten action slots, with

$$
Q(s,a)\leftarrow Q(s,a)+\alpha\left[r+\gamma\max_{a'}Q(s',a')-Q(s,a)\right],
$$

\(\alpha=0.15\), \(\gamma=0.98\), and \(\epsilon\) annealed from 0.35 to 0.02 over 3,000 episodes.

**Hybrid.** Hybrid-1 keeps the policy's top three actions and evaluates each with the depth-1 search value. A good prior makes search cheap; a bad one can prune the right action.

## 5. Experimental Protocol

**Side-swapped matches on a common schedule.** A comparison is defined by a schedule \(\{(T_0^{(g)},T_1^{(g)},\xi_g)\}_{g=1}^G\), generated once from a protocol seed and shared by every agent. Each entry is played twice, once per side; both games use the same team pair but independent battle seeds (\(\xi_g\), \(\xi_g+1\)). The `match` helper enforces this pairwise; `round_robin` passes the same protocol seed to every pair, so all pairs see the same team schedule. Win rate is \(\hat p=W/(W+L)\), with draws excluded.

**Bootstrap intervals.** The reported interval is a percentile bootstrap over Bernoulli resamples, \(\hat p_b^*\sim\mathrm{Binomial}(n,\hat p)/n\), with \(B=2{,}000\) and \(n=W+L\). It captures binomial noise but not correlation between the two orientations of a pair or variance across training seeds. At \(n=120\) the normal-approximation half-width is 8.9 points, so 120-game matches are underpowered for small effects. The reference run uses 120 side-swapped games per pair in the round robin and 100 games for the search-2 oracle match.

**Bradley-Terry ratings.** Pairwise results are fit with \(\Pr(i\text{ beats }j)=p_i/(p_i+p_j)\) using the MM algorithm for 500 iterations; draws count as half a win each. Ratings use \(R_i=400\log_{10}p_i+1000\). The model assumes transitive, stationary strengths and independent matches. Ratings are descriptive, not a significance test; the reference round robin is configured for six agents and 15 comparisons, with no multiplicity correction.

**Held-out species split.** Training excludes **Volcarona (bug/fire), Hydreigon (dark/dragon), Toxapex (poison/water), Clefable (fairy), Zeraora (electric), and Corviknight (flying/steel)**. Learners train on `TRAIN_SPECIES`; `match` defaults to `ALL_SPECIES`, so the caller must pass the held-out pool. The split is defined by species, but Dark and Fairy appear only on held-out species, so it also tests unseen defensive typings, and a gap cannot be attributed to species novelty alone. Report held-out win rate, top-1 agreement with search labels, and the same quantities on training states.

**Compute and seeds.** Report wall-clock, games/s, decisions/s, training time, and parameter count, single-threaded on `Intel64 Family 6 Model 141 Stepping 1, GenuineIntel` with `3.12.10`. The reference run uses one training seed (2025) and a fixed evaluation schedule; a multi-seed replication is future work. REINFORCE checkpoint selection, where used, evaluates every 250 episodes and keeps the best checkpoint.

## 6. Results

Tables are generated by the reference run from `results/*.json` via `python -m pokerl report`; they are not hand-typed.

**Leaderboard** (rating, W-L-D, win rate with 95% CI, throughput; primary comparison vs Heuristic).

| Agent | Elo | W–L–D | Win rate | 95% CI | Decisions/s |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Search-1** | 1153 | 429–158–13 | 73.1% | [69.3, 76.7] | 445 |
| **Heuristic** | 1104 | 392–204–4 | 65.8% | [61.9, 69.6] | 3827 |
| **Greedy** | 1073 | 363–230–7 | 61.2% | [57.3, 65.1] | 4078 |
| **MLP BC** | 943 | 242–348–10 | 41.0% | [37.1, 44.9] | 2519 |
| **MLP+DAgger** | 913 | 214–375–11 | 36.3% | [32.6, 40.2] | 2585 |
| **Random** | 813 | 134–459–7 | 22.6% | [19.4, 26.1] | 4171 |

The six-agent round robin separates the rule-based, search, and learned policies. Search-1 is the strongest runnable agent (73.1% overall, 69.5% head-to-head against Heuristic) at roughly 500 decisions/s. Search-2 reaches 90.0% against Heuristic at 30.9 decisions/s in a separate 100-game match. MLP BC reaches 41.0% overall (37.5% against Heuristic) at roughly 2.5k decisions/s; DAgger reaches 36.3% overall (40.0% against Heuristic). Search depth is the dominant strength lever; distillation buys throughput at a large strength cost.

**Learning curves** (BC budgets, REINFORCE checkpoints, win rate vs Heuristic).

| Stage | Budget | Win rate vs Heuristic |
| --- | ---: | ---: |
| BC (search labels) | 500 decisions | 3.8% |
| BC (search labels) | 1000 decisions | 6.2% |
| BC (search labels) | 2000 decisions | 3.8% |
| BC (search labels) | 3006 decisions | 0.0% |


The BC curve above uses the **linear** policy as a deliberately weak negative control. The non-linear MLP reaches 41.0% overall (37.5% against Heuristic) in the leaderboard; the linear model never learns a useful action ranking.

**Generalization** (train- vs held-out-species win rate and \(\Delta\)).

| Agent | Train species win rate | Held-out species win rate | Δ |
| --- | ---: | ---: | ---: |
| **Heuristic** | 54.1% | 63.6% | +9.6 pp |
| **Search-1** | 64.6% | 78.0% | +13.4 pp |
| **MLP BC** | 37.4% | 14.3% | -23.1 pp |
| **Hybrid-1** | 66.0% | 66.0% | -0.0 pp |
| **MLP+DAgger** | 30.2% | 17.0% | -13.2 pp |

**Efficiency** (mean decisions/s and relative cost).

| Agent | Elo | Mean decisions/s | Relative cost |
| --- | ---: | ---: | ---: |
| **Search-1** | 1153 | 445 | 9.4× |
| **Heuristic** | 1104 | 3827 | 1.1× |
| **Greedy** | 1073 | 4078 | 1.0× |
| **MLP BC** | 943 | 2519 | 1.7× |
| **MLP+DAgger** | 913 | 2585 | 1.6× |
| **Random** | 813 | 4171 | 1.0× |

### 6.1 What would falsify this

- **Determinism.** A replay mismatch on the same build (winner, turns, or log) falsifies the determinism claim.
- **Discrimination.** If all pairwise intervals overlap, or the Bradley-Terry fit is unstable under small schedule perturbations, the roster does not separate policies and the leaderboard is uninformative.
- **Lookahead.** If Search-1 does not beat Heuristic with a clear interval, or Search-2 is not better than Search-1, the claim that the heuristic opponent model plus depth adds decision quality is false.
- **Learning and generalization.** If Linear BC, MLP BC, DAgger, and REINFORCE all fail to beat Heuristic on held-out species, the pipeline does not improve decisions even if training loss falls. If held-out performance is indistinguishable from Random while in-distribution performance is high, the split measures memorization; if the two are indistinguishable, the split is not testing a meaningful shift.
- **Efficiency and richness.** If measured throughput makes the stated sample size impractical, the "cheap benchmark" claim fails; if removing crits, accuracy, and damage rolls leaves the leaderboard unchanged, outcome variance is not driven by the mechanics the benchmark claims to study.

## 7. Limitations and Failure Modes

**Mechanics coverage.** The engine omits weather, terrain, multi-hit moves, screens, confusion/flinch/Taunt/Encore/Substitute/Leech Seed, and most items and abilities; it has one hazard layer and a partial ability set. Declared abilities beyond that set are inert (Section 3.3).

**Full observability.** Version 1 exposes the opponent's full team, moves, PP, item, and ability. It does not test belief modeling, bluffing, or hidden-information planning; uncertainty is stochastic and strategic, not informational. This is the largest gap to cartridge/Showdown play; masking fields would not help because the feature map uses them.

**Fixed sets and small roster.** There is no teambuilding, team preview, or set variation. The 24-species roster covers 17 of 18 types, has no Rock-type, and has only one Dark-type and one Fairy-type, both held out. Sampled matchups let type coverage and composition dominate a small sample; side-swapping mitigates but does not remove this. Species-level conclusions do not generalize to the full Pokédex.

**Heuristic opponent model and stochastic search.** Search assumes the opponent samples from the top-3 heuristic actions at temperature 18: a model, not a Nash equilibrium. Search can exploit blind spots; depth can compound model error. It integrates over opponent actions but samples transition noise once per branch, so values are noisy. Full transition expectimax would multiply the branching factor.

**Draws, scope, and power.** Draws are excluded from win rate and half-weighted in Bradley-Terry; the 100-turn HP tiebreak can reward passivity, and the 300-decision cap would draw if it bound. The benchmark is 1v1/3v3; 6v6, doubles, and preview are out of scope. The bootstrap is parametric and ignores pair correlation; 15 comparisons get no multiplicity correction; one training seed leaves seed variance unestimated. A cluster bootstrap and hierarchical Bradley-Terry model would be better.

**Implementation and reproducibility.** The suite covers RNG, types, stats, engine branches, features, agents, evaluation, reporting, dispatch, CLI, and replay (54 tests). Secondary effects and ability interactions are not exhaustive (FAILURES.md). Policy JSON omits feature-name hashes, so a dimension-preserving change can reuse incompatible weights. `config_hash` covers only the supplied payload, not Git or versions. The split is caller-enforced; a careless `match` can leak held-out species. REINFORCE is undiscounted, checkpoint selection optimistic, and there is no human/LLM baseline.

## 8. Reproducibility

Commands use the `python -m pokerl` CLI (`pokerl` after install); `experiments/run_all.py` runs the reference sequence.

```bash
python -m pokerl train --seed 2025
python -m pokerl bench --games 120 --seed 2025
python -m pokerl report
```

```python
# replay.py: determinism check
from pokerl.agents import HeuristicAgent, RandomAgent
from pokerl.engine import Battle
from pokerl.rng import RNG


def replay(seed: int):
    b = Battle(["garchomp", "dragonite", "metagross"], ["blissey", "skarmory", "gliscor"], seed=seed)
    a0, a1 = HeuristicAgent(), RandomAgent()
    r0, r1 = RNG(seed ^ 0xAA55), RNG(seed ^ 0x55AA)
    while not b.done:
        b.step(a0.act(b, 0, r0), a1.act(b, 1, r1))
    return b.winner, b.turn, tuple(b.log)


assert replay(11) == replay(11)
```

**Artifacts.** The reference run writes under `results/`: `leaderboard.json` (standings, matches, metadata), `training.json` (budgets, losses, win rates), `learning_curve.json`, `generalization.json`, `oracle.json`, `metadata.json`, and `REPORT.md`; it also writes `docs/assets/*.svg`. Policy weights live under `artifacts/` (`policy_bc.json`, `policy_mlp.json`, and `policy_dagger.json` when DAgger is enabled). `experiments/run_all.py` is the reference pipeline; `results/run.log` is its transcript.

**Config hash.** `pokerl.train.config_hash` computes SHA-256 over `json.dumps(payload, sort_keys=True)` and truncates to 16 hex characters. Include the package version, sorted species IDs, held-out split, feature-name list, hyperparameters, and seed set. It is a content identifier, not a signature.

**Dependencies.** The runtime package imports only the standard library. `torch` is imported lazily inside `train_mlp_bc`; the exported MLP uses NumPy when available and a pure-Python fallback otherwise. "Dependency-free" means zero third-party runtime dependencies, not zero interpreter. The package requires Python 3.11+ (`datetime.UTC` and modern typing); the reference environment is CPython 3.12.

**Reproducibility status.** The engine and evaluation suite are covered by 54 tests, deterministic replay is checked in CI, and the reference pipeline writes results under `results/` and `artifacts/`. The Dockerfile and devcontainer pin a Python 3.12 environment. The remaining gap is cross-platform floating-point determinism: the RNG is platform-independent, but damage uses floats and `math.exp`, so libm differences can change a damage roll. The reference numbers are for CPython 3.12 on the reported platform.

## 9. Ethics and Impact

PokéLab is a benchmark, not a deployment. Its agents are research artifacts; a high rating does not imply skill at cartridge Pokémon, 6v6, doubles, or any real-world task. The roster is a narrow slice, and conclusions about "Pokémon ability" from a 24-species, full-information, fixed-set game would be a category error.

Pokémon and Pokémon character names are trademarks of Nintendo, Creatures Inc., GAME FREAK inc., and The Pokémon Company. This project is not affiliated with, endorsed by, or sponsored by any of them. The `pokerl` package contains no ROMs, ripped sprites, or game assets; it uses names and hand-curated stat lines for research. It involves no human subjects, personal data, or online play, and it should not be used to gain an unfair advantage in competitive play. Compute costs are small but nonzero; report them. A future LLM text interface needs its own validity and contamination analysis; a PokéLab score would not be evidence of general capability.

## Appendix A. Feature List Summary

The map has 188 dimensions per legal action: 51 action, 120 global, and 17 interaction features.

**Action (51).** Identity, type one-hot, category, power, accuracy, priority, contact, recoil/drain, fixed damage, heal, setup, hazard, clear, Protect, pivot, STAB, effectiveness, expected damage, can-KO, boost/drop, status chance, PP, and six incoming-switch features (HP, type/speed advantage, Regenerator, Natural Cure, status).

**Global (120).** Twenty-three scalars (HP, alive, speed, boosts, statuses, hazards, turn, bench HP, type advantage, Choice/Regenerator/Levitate); 36 type one-hots; 10 stats; 10 status one-hots; 10 boosts; 10 item flags; 16 ability flags; five threat scalars.

**Interactions (17).** Products of action and state terms: power × effectiveness, power × own HP, priority × speed deficit, heal × missing HP, setup × own HP, status × opponent-clean, hazard × missing hazard, switch × matchup, damage/KO × opponent HP, effectiveness × STAB, and Protect/switch/status interactions.

## Appendix B. Engine Invariants

1. **Replay and clone isolation.** Same build, seed, and actions produce the same winner, turns, and log; `clone()` deep-copies teams and RNG and never mutates the parent.
2. **Legal-action closure.** `step` validates both actions and raises on illegal ones; no fainted or zero-PP moves.
3. **Turn order.** Switches precede moves; moves resolve by priority, effective speed, then a random tie-break; a fainted side does not act.
4. **HP, faint, and PP.** HP stays in \([0,\mathrm{maxHP}]\); fainted implies HP \(=0\); zero living Pokémon loses; Struggle is legal only when no move or switch is.
5. **Choice lock.** A Choice item locks the last move; switching clears the lock; a locked move with zero PP falls back to switch/Struggle.
6. **Status and stages.** At most one major status; immunities are checked first; sleep lasts 1–3 turns; stages are clamped to \([-6,6]\), reset on switch, and crits ignore the attacker's negative and defender's positive stages.
7. **Hazards.** One Stealth Rock layer; damage is \(\mathrm{maxHP}\times\text{rock effectiveness}/8\), blocked by Heavy-Duty Boots and Magic Guard, cleared by Defog (both sides) or Rapid Spin (own side, \(+1\) Speed).
8. **Terminal states.** One side empty: other wins. Both empty: draw. Turn 100: larger team HP fraction wins; exact tie draws. Winner \(-1\) gives reward \(0\); otherwise \(+1/-1\).
9. **Observability and scope.** `BattleView` exposes both sides' full team, moves, PP, item, and ability; the engine accepts six, but the protocol is 1v1 and 3v3.
