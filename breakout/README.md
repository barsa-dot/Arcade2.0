# Breakout – Dynamic Speed Edition

A modernized, retro-styled **Breakout** arcade game built with Python and Pygame. Features dynamic ball speed scaling, procedural audio synthesis, multiple power-up drops, dynamic level designs, and dynamic combo scoring.

---

## Features

* **Dynamic Speed Mechanics:** Ball speed increases continuously over time (+0.1 speed units/second) and scales with each level.
* **Procedural Sound Effects:** Built-in real-time audio synthesizer generated directly using NumPy/math math operations without external sound asset dependencies.
* **Power-Up System:** Drops include:
  * **Wide Paddle (W):** Expands paddle size temporarily.
  * **Multi-Ball (M):** Spawns an extra ball into play.
  * **Slow-Motion (S):** Reduces ball velocity temporarily.
  * **Extra Life (+):** Grants an additional life.
* **Varied Level Layouts:** Randomly generated block patterns across levels (Full grid, Checkerboard, Pyramid, and Gapped layouts) with multi-hit and special golden high-value bricks.
* **Visual Effects:** Particle explosion effects on brick destruction, score popups, combo counters, and ball particle motion trails.

---

## Tech Stack

* **Language:** Python 3.x
* **Game Engine:** Pygame

---

## Project Structure

```text
breakout/
├── main.py              # Main application entry point & game logic
├── requirements.txt      # Project dependencies
└── README.md             # Documentation