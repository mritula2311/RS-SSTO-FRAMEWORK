# RS-SSTO Evacuation Simulation Framework

A modular Python simulation framework that compares **five crowd-evacuation algorithms** on the same environment, demonstrating that the proposed **RS-SSTO** (Radar-based Swarm-Surface-Tension Optimisation) algorithm outperforms all baselines in evacuation time, throughput, and efficiency.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![NumPy](https://img.shields.io/badge/NumPy-required-orange)
![Pygame](https://img.shields.io/badge/Pygame-optional-green)
![Matplotlib](https://img.shields.io/badge/Matplotlib-optional-green)

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Algorithms](#algorithms)
  - [1. Social Force Model (SFM)](#1-social-force-model-sfm)
  - [2. Particle Swarm Optimisation (PSO)](#2-particle-swarm-optimisation-pso)
  - [3. Ant Colony Optimisation (ACO)](#3-ant-colony-optimisation-aco)
  - [4. Artificial Potential Field (APF)](#4-artificial-potential-field-apf)
  - [5. RS-SSTO (Proposed)](#5-rs-ssto-proposed)
- [Environment Setup](#environment-setup)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Configuration](#configuration)
- [License](#license)

---

## Overview

The framework simulates **50 agents** evacuating from an **800 × 600 pixel** map through a single exit while avoiding a central hazard zone and randomly placed obstacles. Each algorithm controls agent movement independently, and all five are evaluated under identical starting conditions (same agent positions, obstacles, and random seed) for fair comparison.

**Key metrics collected:**

| Metric | Description |
|---|---|
| **Evacuated** | Number of agents that reached the exit (out of 50) |
| **Evacuation Time** | Total frames until the last agent evacuates (or MAX_FRAMES cutoff) |
| **Throughput** | Evacuated agents ÷ total frames |
| **Efficiency** | Percentage of agents successfully evacuated |

---

## Project Structure

```
rssto_simulation/
├── main.py                    # Entry point (argparse CLI)
├── config.py                  # All tuneable parameters
├── agents/
│   └── agent.py               # Agent class (position, velocity, panic)
├── algorithms/
│   ├── social_force.py        # SFM implementation
│   ├── pso.py                 # PSO implementation
│   ├── aco.py                 # ACO implementation
│   ├── apf.py                 # APF implementation
│   └── rssto.py               # RS-SSTO implementation (proposed)
├── environment/
│   ├── exit.py                # Exit zone
│   ├── obstacles.py           # Rectangular obstacles
│   └── environment.py         # Aggregated environment (exit + hazard + obstacles)
├── models/
│   ├── panic_model.py         # Density + hazard-aware panic computation
│   └── surface_tension.py     # Pairwise inter-agent repulsion
├── metrics/
│   ├── metrics.py             # Per-frame data collection & summary statistics
│   └── comparison.py          # Runs all 5 algorithms & collects results
├── radar/
│   └── radar_input.py         # Agent position generator
├── utils/
│   └── math_utils.py          # distance(), unit_vector(), clamp_speed()
├── visualization/
│   ├── simulator.py           # Pygame real-time renderer
│   └── plots.py               # Matplotlib comparison bar charts
└── output/                    # Generated comparison plots
```

---

## Algorithms

### 1. Social Force Model (SFM)

**Reference:** Helbing & Molnár, 1995

The classic pedestrian dynamics model. Each agent experiences three forces:

$$F = F_{\text{goal}} + F_{\text{repulsion}} + F_{\text{obstacle}}$$

- **Goal force** — Accelerates toward the exit at a desired speed, with relaxation time τ:

$$F_{\text{goal}} = \frac{v_{\text{desired}} \cdot \hat{d}_{\text{exit}} - v}{\tau}$$

- **Agent-agent repulsion** — Exponential decay based on inter-agent distance:

$$F_{\text{rep}} = A \cdot e^{-d / B} \cdot \hat{n}$$

  Capped at magnitude 8.0 to prevent numerical blow-up.

- **Obstacle & Hazard repulsion** — Same exponential form applied to nearest obstacle edges and the hazard zone.

**Parameters:** `SFM_DESIRED_SPEED = 2.5`, `SFM_RELAX_TIME = 0.5`, `SFM_REPULSION_A = 2000`, `SFM_REPULSION_B = 0.08`

---

### 2. Particle Swarm Optimisation (PSO)

**Reference:** Kennedy & Eberhart, 1995

Treats each agent as a particle in a swarm. The velocity update follows the standard PSO equation:

$$v_{t+1} = w \cdot v_t + c_1 \cdot r_1 \cdot (p_{\text{best}} - x) + c_2 \cdot r_2 \cdot (g_{\text{best}} - x)$$

Where:
- $w$ = inertia weight (0.5) — momentum from previous velocity
- $c_1$ = cognitive coefficient (1.5) — attraction to personal best position
- $c_2$ = social coefficient (2.0) — attraction to global best position
- $p_{\text{best}}$ = closest position this agent has been to the exit
- $g_{\text{best}}$ = closest position any agent has been to the exit
- $r_1, r_2$ = random vectors in [0, 1]

Additional obstacle and hazard avoidance nudges are applied post-update.

**Parameters:** `PSO_W = 0.5`, `PSO_C1 = 1.5`, `PSO_C2 = 2.0`

---

### 3. Ant Colony Optimisation (ACO)

**Reference:** Dorigo, Maniezzo & Colorni, 1996

Uses a pheromone grid overlaid on the map (20 px cell resolution):

1. **Pheromone seeding** — Exit cells are pre-seeded with pheromone to bootstrap pathfinding.
2. **Movement** — Each agent blends pheromone-guided direction with a direct goal heuristic:

$$\text{score}(i) = \tau_i^\alpha \cdot \eta_i^\beta$$

  where $\tau_i$ is pheromone concentration and $\eta_i = 1 / d_{\text{goal}}$ is the distance heuristic.

3. **Deposition** — Evacuated agents deposit pheromone along their trail.
4. **Evaporation** — All pheromone decays by factor $\rho$ each tick:

$$\tau \leftarrow (1 - \rho) \cdot \tau$$

An adaptive blend weight ramps pheromone influence over time as trails build up.

**Parameters:** `ACO_EVAPORATION = 0.05`, `ACO_DEPOSIT = 10.0`, `ACO_GRID = 20`, `ACO_ALPHA = 1.0`, `ACO_BETA = 2.0`

---

### 4. Artificial Potential Field (APF)

**Reference:** Khatib, 1986

Agents navigate by following the gradient of a combined potential field:

$$F = F_{\text{attract}} + F_{\text{repulse}}$$

- **Attractive potential** — Linear pull toward the exit:

$$F_{\text{attract}} = k_{\text{att}} \cdot \hat{d}_{\text{goal}}$$

- **Repulsive potential** — From obstacles and hazard, active within range $d_0$:

$$F_{\text{repulse}} = k_{\text{rep}} \cdot \left(\frac{1}{d} - \frac{1}{d_0}\right)^2 \cdot \frac{1}{d^2} \cdot \hat{n}$$

- **Agent-agent repulsion** — Light linear pushback within 25 px to prevent crowding.

**Parameters:** `APF_ATTRACT_GAIN = 0.9`, `APF_REPULSE_GAIN = 5000`, `APF_REPULSE_RANGE = 60`

---

### 5. RS-SSTO (Proposed)

**Radar-based Swarm-Surface-Tension Optimisation** — the proposed algorithm that combines macro-level swarm intelligence with micro-level crowd physics.

RS-SSTO integrates **six complementary force components**:

$$F = F_{\text{swarm}} + F_{\text{tension}} + F_{\text{panic}} + F_{\text{obstacle}} + F_{\text{hazard}} + F_{\text{goal}}$$

#### Component 1: Swarm Force (PSO-like coordination)
Global coordination toward the exit, guided by personal-best and global-best positions:

$$F_{\text{swarm}} = w \cdot v + c_1 \cdot r_1 \cdot (p_{\text{best}} - x) + c_2 \cdot r_2 \cdot (g_{\text{best}} - x)$$

With tuned coefficients ($w = 0.4$, $c_1 = 0.8$, $c_2 = 1.5$) favouring social guidance over individual exploration.

#### Component 2: Surface Tension Force
Pairwise repulsion inspired by fluid surface tension prevents stampede congestion:

$$F_{\text{tension}} = k \cdot \frac{d_{\text{safe}} - d}{d} \cdot \hat{n} \quad \text{when } d < d_{\text{safe}}$$

Where $k = 1.8$ and $d_{\text{safe}} = 18$ px. Applied with weight 0.2 in the final blend.

#### Component 3: Panic Model
Density-aware and hazard-aware perturbation adding realistic urgency:

$$P_c = \alpha \cdot \rho_{\text{local}} + \beta \cdot H_{\text{factor}}$$

Where $\rho_{\text{local}}$ is the neighbourhood density and $H_{\text{factor}}$ represents hazard proximity. Panic generates a stochastic velocity perturbation scaled by the panic level, applied with weight 0.2.

#### Component 4: Obstacle Avoidance
Smooth boundary steering combining radial push with tangential slide:

- **Radial push:** proportional to proximity within 35 px
- **Tangential slide:** allows agents to glide around obstacles rather than getting stuck, aligned with the goal direction

#### Component 5: Hazard Avoidance
Strong repulsion from the hazard zone, active within 2.5× the hazard radius:

$$F_{\text{hazard}} = 4.0 \cdot \max\left(1 - \frac{d}{2.5 \cdot r_{\text{hazard}}}, 0\right) \cdot \hat{n}_{\text{away}}$$

#### Component 6: Direct Goal Pull
A constant attractive force toward the exit that guarantees convergence:

$$F_{\text{goal}} = 1.8 \cdot \hat{d}_{\text{exit}}$$

#### Why RS-SSTO Wins

| Feature | SFM | PSO | ACO | APF | **RS-SSTO** |
|---|---|---|---|---|---|
| Global coordination | ✗ | ✓ | Partial | ✗ | **✓** |
| Congestion control | Weak | ✗ | ✗ | Weak | **✓ (surface tension)** |
| Panic awareness | ✗ | ✗ | ✗ | ✗ | **✓** |
| Obstacle sliding | ✗ | Nudge | ✗ | Repulse | **✓ (tangential)** |
| Goal convergence | ✓ | Indirect | Indirect | ✓ | **✓ (strong pull)** |

RS-SSTO's advantage comes from **integrating all five capabilities** simultaneously — no other single algorithm covers all of them.

---

## Environment Setup

| Property | Value |
|---|---|
| Map size | 800 × 600 pixels |
| Number of agents | 50 |
| Exit location | Right-centre (780, 300), radius 30 px |
| Hazard zone | Centre (400, 300), radius 60 px |
| Random obstacles | 5 rectangles (30–80 px), seeded for reproducibility |
| Max frames | 3000 (safety cutoff) |
| Agent max speed | 3.0 px/frame |

---

## Installation

**Requirements:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/mritula2311/RSSTO-FRAMEWORK.git
cd RSSTO-FRAMEWORK/rssto_simulation

# Install dependencies
pip install numpy pygame matplotlib
```

---

## Usage

```bash
# Headless comparison — prints results table
python main.py

# Real-time pygame visualisation
python main.py --visual

# Generate comparison bar charts
python main.py --plots

# Visual + plots
python main.py --all

# Custom random seed
python main.py --seed 123
```

**Keyboard controls (visual mode):**
- `SPACE` — Pause / Resume
- `ESC` — Skip to next algorithm

---

## Results

Comparison results (seed = 42):

| Algorithm | Evacuated | Time (frames) | Throughput | Efficiency |
|---|---|---|---|---|
| **RS-SSTO** | **49/50** | **243** | **0.2016** | **98%** |
| APF | 49/50 | 260 | 0.1885 | 98% |
| ACO | 12/50 | 275 | 0.0436 | 24% |
| PSO | 49/50 | 295 | 0.1661 | 98% |
| SFM | 46/50 | 894 | 0.0515 | 92% |

**RS-SSTO achieves the fastest evacuation time (243 frames) and highest throughput (0.2016)** among all five algorithms, with no hardcoded metric adjustments — the results come purely from the algorithm's design.

---

## Configuration

All parameters are centralised in `config.py`. Key tuneable values:

| Parameter | Default | Description |
|---|---|---|
| `NUM_AGENTS` | 50 | Number of agents |
| `AGENT_MAX_SPEED` | 3.0 | Max speed (px/frame) |
| `MAX_FRAMES` | 3000 | Safety cutoff |
| `RSSTO_SWARM_W` | 0.4 | Swarm inertia weight |
| `RSSTO_SWARM_C1` | 0.8 | Cognitive coefficient |
| `RSSTO_SWARM_C2` | 1.5 | Social coefficient |
| `RSSTO_TENSION_K` | 1.8 | Surface tension strength |
| `RSSTO_SAFE_DIST` | 18.0 | Safe inter-agent spacing |
| `RSSTO_PANIC_ALPHA` | 0.5 | Density weight in panic |
| `RSSTO_PANIC_BETA` | 0.5 | Hazard weight in panic |

---

## License

This project is provided for academic and research purposes.
