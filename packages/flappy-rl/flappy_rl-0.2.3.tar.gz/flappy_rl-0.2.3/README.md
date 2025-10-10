# 🏆 FlappyAlpha: Reinforcement Learning vs Human

[![PyPI version](https://badge.fury.io/py/flappy-rl.svg)](https://badge.fury.io/py/flappy-rl)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎮 Overview

**FlappyAlpha** is a reinforcement learning (RL) project inspired by AlphaGo, where an RL agent learns to play a custom Flappy Bird game environment with realistic physics (gravity, collision, etc.). The agent (FlappyAlpha) is trained using Q-Learning to maximize its score by passing obstacles and avoiding crashes. The project also features human vs. agent battles to showcase the agent's learning progress.

## 🎮 Features

- Custom Flappy Bird environment built with Pygame
- Q-Learning agent with reward/punishment system
- RL training for "Beginner" and "Hard" agents
- Human vs Agent battle playground with score visualization
- Performance interpretation and result plots
- Easy to use and play for normal users (a PyPI package is prepared)

## 🎮 Tech Stack

- **Game & UI:** Python, Pygame
- **Reinforcement Learning:** Q-Learning (NumPy)
- **Data Analysis & Result Visualization:** NumPy, Matplotlib

## 🎮 Simple Demo
![Demo video](<https://raw.githubusercontent.com/kaifeng-cmd/zephyra/refs/heads/main/src/flappy_rl/assets/Screen Recording 2025-02-23 170420.gif>)

## 📂 Project Structure

The project uses a standard `src` layout to separate the installable package from developer scripts.

```
zephyra/
│
├── .github/workflows/      # CI/CD pipeline for PyPI publishing
├── src/
│   └── flappy_rl/          # Core package source code
│       ├── game/           # Game environment logic
│       ├── models/         # Pre-trained Q-table models (.npy)
│       ├── assets/         # Game assets
│       ├── __init__.py
│       └── main.py         # Entry point for PyPI package to run
│
├── scripts/                # Scripts for developers (training, testing)
│   ├── train_qLearningBEGINNER.py
│   ├── train_qLearningHARD.py
│   ├── playground.py
│   └── playgroundHARD.py
│
├── results/                # Output for training & playing result graphs
├── LICENSE
├── pyproject.toml          # Main project configuration for packaging
├── README.md
└── requirements.txt        # Dependencies
```

---

## 🚀 Quick Start (For Users that are just want to play only)

Get started in under a minute! Play against the AI directly from your terminal. I've make it as an offical python package.

![carbon](https://raw.githubusercontent.com/kaifeng-cmd/zephyra/refs/heads/main/screenshots/carbon.png)

### 1. Install from PyPI
```bash
pip install -U flappy-rl
```

### 2. Challenge the Agent
- Play against the **Beginner** agent:
  ```bash
  flappy-alpha --mode beginner
  ```
- Play against the **Hard** agent:
  ```bash
  flappy-alpha --mode hard
  ```
### Example
![cmd to start the game](https://raw.githubusercontent.com/kaifeng-cmd/zephyra/refs/heads/main/screenshots/cmdtoStart.png)

---

## 🛠️ For Developers & Researchers

This section is for those who want to dive deeper, retrain the models, or experiment with the code.

### 1. Clone the Repository
```bash
git clone https://github.com/kaifeng-cmd/zephyra.git
cd zephyra
```

### 2. Install Dependencies
It's recommended to use a virtual environment.
```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv

# For Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Train the RL Agent
Pre-trained models are included, but you can start your own training sessions.

- Train the Beginner agent (2500 episodes):
  ```bash
  python scripts/train_qLearningBEGINNER.py
  ```
- Train the Hard agent (3000 episodes):
  ```bash
  python scripts/train_qLearningHARD.py
  ```
  > Training progress and results will be saved as `.png` plots in the `results/` folder.

### 4. Run the Playground
Test the agents or play against them using the original developer scripts.

- Play against the Beginner agent:
  ```bash
  python scripts/playground.py
  ```
- Play against the Hard agent:
  ```bash
  python scripts/playgroundHARD.py
  ```

---

## 🎮 Highlights & Insights

- The RL agent receives positive rewards for passing pipes/blocks and negative penalties for crashing.
- As training episodes increase, the agent's performance improves dramatically:
  - After 2500 episodes `(beginner mode)`: Best score 17.
  - After 3000 episodes `(hard mode)`: Best score 75 (441% increase).
  - After 4000 episodes: Best score 3693 (near-perfect play).
  > U can modify the training parameter, ex. EPISODES = 4000 if u want.
- Human players can easily beat the Beginner agent `(2500 episodes)`, but the Hard agent `(3000 episodes)` is a tough opponent, often outperforming humans in average score, and I'm sure for `> 4000 episodes` training, human can't beat RL agent as it plays near perfect.

## 🎮 Acknowledgements

Inspired by AlphaGo and the power of reinforcement learning.

---

<div align="center">
  <p>💎 <em>Feel free to fork, do experiment, and challenge FlappyAlpha.</em></p>
</div>