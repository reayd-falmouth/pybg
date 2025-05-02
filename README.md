# 🧠 PyBG

**ASCIIGammon RL** is a feature-rich, gym-compatible Backgammon environment built for reinforcement learning, AI training, and human play. It includes complete implementations of match logic, game rules (Backgammon, Nackgammon, Acey-Deucy), and ASCII-based rendering.

---

## 🎮 Features

- ✅ Full Backgammon match logic (dice, cube, doubling, resignations)
- 🔁 Support for Backgammon, Nackgammon, and Acey-Deucy
- 🧠 Gymnasium-compatible RL environment
- 🧱 Board, Match, and Position encoded/decoded via GNUBG-compatible IDs
- 📈 Observation and action spaces, valid action masks
- ♻️ Swap perspective logic for self-play and evaluation
- 🧾 ASCII-rendered board with rich game state info

---

## 🛠️ Installation

```bash
pip install -e .
```

Requirements include:
- `gymnasium`
- `numpy`

---

## 🚀 Quick Start

```python
from pybg.core.board import Board

env = Board()
obs, info = env.reset()

done = False
while not done:
   action = env.action_space.sample()
   obs, reward, done, truncated, info = env.step(action)
   env.render()
```

---

## 🔧 Components

- `Board` – Main RL environment and gameplay engine.
- `Match` – Encodes match state, cube value, scores, turn, and game progression.
- `Position` – Encodes/decodes the board into a compact string ID and handles move logic.

---

## 🧪 Example Encodings

```python
from pybg.core.match import Match
from pybg.core.position import Position

match = Match.decode("cAgAAAAAAAAA")
position = Position.decode("4HPwATDgc/ABMA")

match_id = match.encode()
position_id = position.encode()
```

---

## 🧠 Observation Space

The observation includes:
- Dice values
- Bar and borne-off counts
- Encoded board points (player and opponent)

## 🎯 Action Space

Actions include:
- Rolling, doubling, resigning, accepting/rejecting resignations
- Legal moves derived from current dice roll
- Action masking for invalid move pruning

---

## 📈 Rendering

ASCII rendering provides a human-readable board with:
- Checkers on points
- Dice, cube, score, pip count
- Player names and game status

---

## 🤖 Reinforcement Learning Ready

The environment is compatible with common RL libraries like Stable-Baselines3 or CleanRL, using discrete or continuous action spaces and optional action masking.

---

## 📜 License

MIT License.