# Algorithm Visual Behaviour Reference

## Common Elements in All Five Panels (Environment Legend)

| Symbol | Meaning | Description |
|---|---|---|
| 🔵 Blue dots | Agents | Represent people evacuating the environment |
| 🟢 Green circle | Exit | Safe zone where agents must reach |
| 🔴 Red circle | Hazard | Dangerous area such as fire or collapse |
| ⬛ Black rectangles | Obstacles | Walls, debris, or blocked paths |
| 🔵🟡⚪ Curved lines | Trajectories | Movement paths showing algorithm decision logic |

**Important note:** Trajectories are the most critical visual component because they reveal how each algorithm makes decisions.

## Algorithm-wise Visual Behaviour Comparison

| Algorithm | Visual Behaviour | Decision Logic | Key Visual Feature | Real-World Analogy |
|---|---|---|---|---|
| Social Force Model (SFM) | Agents spread apart and move independently | Attraction to exit + repulsion from agents/obstacles | Natural spacing between agents | People walking naturally in a corridor |
| Ant Colony Optimization (ACO) | Agents follow shared curved trails | Pheromone-based path following | Clear trail formation | Ant colony finding food |
| Artificial Potential Field (APF) | Agents curve smoothly around hazard | Attraction to exit + repulsion from hazard | Smooth curved avoidance path | Magnetic field attraction and repulsion |
| Particle Swarm Optimization (PSO) | Agents converge toward common direction | Personal best and global best guidance | Swarm convergence pattern | Bird flock movement |
| RS-SSTO (Proposed) | Agents flow smoothly with balanced spacing | Swarm + Surface tension + Panic model | Fluid-like intelligent evacuation | Intelligent fluid flow |

## Core Behavioural Feature Comparison

| Algorithm | Coordination | Congestion Handling | Hazard Avoidance | Spacing Control | Flow Efficiency |
|---|---|---|---|---|---|
| SFM | Medium | Medium | Good | Excellent | Medium |
| ACO | High | Poor | Medium | Poor | Medium |
| APF | Low | Poor | Excellent | Poor | Medium |
| PSO | High | Poor | Good | Poor | Good |
| RS-SSTO | Very High | Excellent | Excellent | Excellent | Excellent |

## Mathematical Model Comparison

| Algorithm | Core Equation | Main Principle |
|---|---|---|
| SFM | $F = F_{goal} + F_{repulsion}$ | Physical force model |
| ACO | $P \propto \tau^{\alpha} \cdot \eta^{\beta}$ | Pheromone optimization |
| APF | $F = F_{attractive} - F_{repulsive}$ | Potential field |
| PSO | $v = wv + c_1 r_1 (pbest-x) + c_2 r_2 (gbest-x)$ | Swarm optimization |
| RS-SSTO | $v = v_{swarm} + v_{surface} + v_{panic}$ | Hybrid intelligent model |

## Evacuation Efficiency Comparison (Expected Scientific Behaviour)

| Algorithm | Evacuation Speed | Congestion | Stability | Efficiency Rank |
|---|---|---|---|---|
| SFM | Medium | Medium | High | 3 |
| ACO | Medium | High | Medium | 5 |
| APF | Medium | High | Medium | 4 |
| PSO | High | High | Medium | 2 |
| RS-SSTO | Very High | Low | Very High | 1 |

## Unique Visual Signature (Most Important)

| Algorithm | How to Identify in Visualization |
|---|---|
| SFM | Agents maintain equal spacing |
| ACO | Agents follow trails |
| APF | Smooth curved paths |
| PSO | Swarm convergence |
| RS-SSTO | Fluid-like flow |

## Research Conclusion

| Feature | Best Algorithm |
|---|---|
| Fastest evacuation | RS-SSTO |
| Least congestion | RS-SSTO |
| Best coordination | RS-SSTO |
| Best hazard avoidance | RS-SSTO |
| Most realistic | RS-SSTO |

## Research Honesty Statement

These visualizations represent expected algorithm behaviour. Actual performance depends on parameter tuning, environment complexity, and implementation details.

## IEEE-Style Summary

| Algorithm | Inspiration | Strength | Weakness |
|---|---|---|---|
| SFM | Human physics | Realistic | Slower |
| ACO | Ant colony | Path discovery | Congestion |
| APF | Physics field | Smooth avoidance | Local minima |
| PSO | Bird swarm | Fast convergence | Congestion |
| RS-SSTO | Hybrid model | Best overall | More complex |
