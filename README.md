# 🧠 PyBG

**PyBG** is a modular framework for developing AI agents that play backgammon and backgammon-like games. It provides a complete environment with match rules, ASCII rendering, RL integration, neural net evaluation, supervised learning tools (GNUBG-compatible), and bearoff endgame databases.

Whether you're building a bot, training reinforcement learning agents, or playing matches with friends, **PyBG** offers a complete, extensible foundation.

---

## ⚙️ Architecture Overview

```
PyBG/
├── core/
│   ├── board.py          # Main game engine (gym.Env compatible)
│   ├── match.py          # Match logic (cube, scores, Crawford rule)
│   ├── position.py       # Board representation and GNUBG-style ID handling
│   ├── bearoff_database.py  # GNUBG one-sided and two-sided bearoff DB interface
│   ├── pub_eval.py       # Fast linear evaluation (Tesauro-style)
│   ├── gnubg_nn.py       # Neural net evaluation from GNUbg .weights
│   ├── eval.py           # Unified evaluation engine with n-ply rollout
│   └── ...
├── assets/
│   └── gnubg/            # Pretrained weights and bearoff files
└── examples/
```

---

## 🎮 Features

* ♟️ **Full Match Engine** — All rules including cube actions, doubling, resignation types, Crawford, Jacoby, and variants (Backgammon, Nackgammon, Acey-Deucy).
* 🧱 **Modular Position & Match Representation** — GNUBG-compatible IDs allow replay, analysis, and supervised training from public data.
* 🧠 **Multi-Modal Evaluation**:

  * Fast **Tesauro-style pub\_eval**
  * Deep **GNUBG neural nets** via `.weights` file
  * **One-sided / two-sided bearoff DBs** for optimal endgame decisions
  * **N-ply recursive evaluation** with opponent modeling
* 🔁 **RL-Ready Environment** — Gymnasium-compatible interface with action masking, legal move sampling, and resettable games.
* 📜 **ASCII UI** — Terminal-based rendering for simple human play.
* 🧪 **Encodable Positions & Match States** — Supports loading/saving via position strings and match IDs.
* 🌐 **(Planned) Online Play + Tutor Mode** — Future support for server play, match review, and explainable move guidance.

---

Evaluation uses:

* Position class (e.g., race/contact/bearoff)
* PubEval or GNUBG neural nets
* 0-ply, 1-ply, and multi-ply lookahead

---

## 🧠 Roadmap for AI Agent Development

> Based on [CompGammon: How to Build a Backgammon Bot](https://compgammon.blogspot.com/p/how-to-make-backgammon-bot.html)

### ✅ Stage 1: Core Framework

* ✅ Build game logic with accurate rule handling
* ✅ Support match progression and legal move generation

### ✅ Stage 2: Position Evaluation

* ✅ Implement fast public evaluator (Tesauro-style)
* ✅ Integrate GNU Backgammon neural nets
* ✅ Add bearoff databases for optimal late-game analysis

### 🔄 Stage 3: Self-Play & RL

* Train reinforcement agents using Gym-compatible interface
* Explore MaskablePPO, AlphaZero-style rollouts

### 🔮 Stage 4: Tutor Mode

* Evaluate best plays with win probabilities
* Show mistake size (centipawn loss) and recommended move

### 🌍 Stage 5: Online Play & Cloud Analysis

* Add socket server for human-vs-human or bot-vs-bot play
* Match logging and postgame review

---

## 🔧 Evaluation Layers (from `eval.py`)

* `PositionClass.OVER` — Game is finished, returns deterministic result
* `PositionClass.BEAROFF1/2` — Uses one-sided or two-sided `.bd` databases
* `PositionClass.RACE/CONTACT/CRASHED` — Uses either pub\_eval or `gnubg_nn`

All evaluations respect ply depth, cache results, and support fallback strategies.

---

## 📈 Development Goals

* ✅ Plug-and-play modules (swap in new net or MET files)
* ✅ Feature-extracted inputs for explainability
* 🚧 External action loggers (SGF, JSON, CSV)
* 🚧 Human-friendly CLI tool (`play.py`, `train.py`, `tutor.py`)
* 🚧 Discord/Telegram bot for turn-based matches

---

## 🧬 Reproducibility & Integration

* Export/import `Position` and `Match` via `.encode()` / `.decode()`
* Store and load cached evaluations with Bearoff DB
* Works with Jupyter, VSCode, and headless servers