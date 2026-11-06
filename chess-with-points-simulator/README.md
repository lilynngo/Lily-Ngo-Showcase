# Chess with Points Simulator

**Game systems · Python · Automated simulation · Statistical balancing**

How much should a custom chess piece cost when it can leap, swap places, protect allies, or otherwise break traditional movement rules?

I built this Python simulator for a two-week University of Washington PCE Game Design assignment in 2026. Its purpose is to explore that balancing question through reproducible matchups, detailed game records, and statistical analysis.

The simulator implements a provided chess variant; this repository showcases my **engineering implementation and experimental methodology**, not authorship of the underlying tabletop game rules.

## At a glance

- **27 piece definitions**, including standard and custom pieces, loaded from JSON.
- **Configurable armies** constrained to 16 pieces (8 Commoners and 8 Nobles) and a 400-point budget.
- **Game rules** covering legal movement, check/checkmate, promotion, and special actions such as swapping, leaping, shielding, and opponent-controlled moves.
- **Batch simulations** with configurable seeds and multiprocessing support.
- **Structured gameplay telemetry** for moves, captures, promotions, special abilities, and outcomes.
- **Balance analysis** using both gameplay-event efficiency metrics and a regularized outcome-based strength estimator.

## How the system works

1. **Configure** piece definitions and legal army compositions.
2. **Simulate** games through a rules engine that validates normal and special actions.
3. **Record** game events and matchup outcomes.
4. **Analyze** piece performance and estimate cost recommendations for further experimentation.

The core design decisions and component map are described in [Architecture & balancing methodology](docs/architecture.md).

## Run a small example

From this folder, with Python 3.10+:

```bash
python -m pip install -r requirements.txt
python -m examples.quick_matchup --games 4 --turns 40 --seed 123
```

The example runs a small standard-army matchup and prints a summary. It deliberately avoids the much larger batch sizes used during balancing experiments.

To run the test suite after installing dependencies:

```bash
python -m pytest -q
```

## Start exploring the code

| Engineering area | Recommended entry point |
| --- | --- |
| Configurable piece and state models | [`src/models.py`](src/models.py), [`src/piece_loader.py`](src/piece_loader.py) |
| Unified legal-action validation | [`src/rules.py`](src/rules.py), [`src/actions.py`](src/actions.py) |
| Recorded match outcomes | [`src/simulation.py`](src/simulation.py), [`src/game_record.py`](src/game_record.py) |
| Seeded, parallel matchup execution | [`src/run_matchup.py`](src/run_matchup.py) |
| Outcome-based piece strength estimation | [`src/report/report_v2.py`](src/report/report_v2.py) |
| Scenario coverage | [`tests/`](tests/) |

## Scope and interpretation

This is a **simulation and analysis tool**, not a playable chess application or a claim that all custom pieces are perfectly balanced. Suggested costs are estimates from particular matchups and assumptions; broader matchup coverage improves their usefulness.

The source files are curated from my development work. Generated spreadsheets, large simulation batches, caches, and third-party artwork are intentionally excluded.
