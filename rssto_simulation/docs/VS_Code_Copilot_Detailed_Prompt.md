# VS CODE COPILOT PROMPT: RS-SSTO Hybrid Algorithm Simulation

## COMPLETE SIMULATION DEVELOPMENT GUIDE

Copy and paste these prompts INTO VS Code Copilot in order. After each prompt, Copilot will generate code. Review it, tweak if needed, then move to next prompt.

---

## PART 1: PROJECT SETUP & DATA STRUCTURES

### Prompt 1.1: Initialize Project Structure

```
I'm building a disaster rescue simulation for the RS-SSTO (Radar-Sensing Surface Tension Optimization) framework.

Create a Python project structure with:
1. Main simulation file: simulation.py
2. Data structures for: Victim, RescueTeam, Disaster, SimulationState
3. Configuration file: config.py with all algorithm parameters
4. Visualization module: visualizer.py for 2D matplotlib animation

Project requirements:
- Use Python 3.8+
- Required libraries: numpy, matplotlib, dataclasses
- Real-time visualization of disaster scenario
- Console logging of optimization progress

Start with __init__.py files and basic directory structure.
Include detailed docstrings explaining each class.
```

### Prompt 1.2: Create Victim and Team Data Structures

```
Create complete data classes for RS-SSTO simulation:

1. Victim class with fields:
   - id: unique identifier
   - x, y: coordinates (meters)
   - z: height (0-100, for multi-floor buildings)
   - classification: enum [CONSCIOUS, UNCONSCIOUS, TRAPPED_IN_RUBBLE, DECEASED]
   - risk_score: 0-1 (higher = more urgent)
   - fusion_confidence: 0-1 (sensor confidence)
   - vital_signs: 0-1 (heartbeat strength)
   - has_received_guidance: boolean
   - group_id: optional (for family tracking)
   - velocity: (vx, vy) for tracking movement
   - assigned_team_id: optional
   - panic_level: 0-1 (will be computed)
   - time_since_detection: float (seconds)

2. RescueTeam class with fields:
   - id: unique identifier
   - x, y: current position
   - current_victim_assignments: list of victim IDs
   - capacity: max victims that can be extracted at once
   - equipment_level: enum [BASIC, STANDARD, ADVANCED]
   - active: boolean
   - total_time_elapsed: tracking time spent
   - victims_rescued: counter

3. Hazard class with fields:
   - id: unique identifier
   - x, y: center position
   - hazard_type: enum [FIRE, COLLAPSE, TOXIC_GAS, FLOOD]
   - radius: danger zone radius
   - intensity: 0-1 (how severe)
   - spread_rate: speed of expansion (m/s)
   - critical_radius: distance within which hazard is fatal

4. SimulationState class to hold:
   - All victims, teams, hazards
   - Current time
   - Optimization history
   - Performance metrics

Include proper initialization, repr methods, and validation.
Add methods for distance calculations using numpy.
```

### Prompt 1.3: Create Configuration File

```
Create config.py with all algorithm parameters organized by category:

PARTICLE SWARM OPTIMIZATION:
- PSO_SWARM_SIZE = 50
- PSO_ITERATIONS = 100
- PSO_INERTIA = 0.7
- PSO_COGNITIVE = 1.5
- PSO_SOCIAL = 1.5

SURFACE TENSION PARAMETERS:
- SURFACE_TENSION = 0.5
- VISCOSITY = 0.2
- PERSONAL_SPACE = 1.5
- VELOCITY_DAMPING = 0.95

PANIC COEFFICIENT:
- PANIC_HAZARD_WEIGHT = 0.6
- PANIC_DENSITY_WEIGHT = 0.4
- PANIC_DECAY_RATE = 0.95
- PANIC_CRITICAL_THRESHOLD = 0.9

SENSOR FUSION:
- RADAR_MAX_RANGE = 500
- THERMAL_MAX_RANGE = 300
- CONFIDENCE_THRESHOLD = 0.7
- FUSION_GRID_SIZE = 10
- STALE_VICTIM_TIMEOUT = 5.0

SIMULATION:
- UPDATE_FREQUENCY = 2.0  # Hz
- SIMULATION_DURATION = 600  # seconds
- WORLD_WIDTH = 500
- WORLD_HEIGHT = 500
- TARGET_DENSITY = 2.0  # persons per m²

Add comments explaining what each parameter does and why it's tuned to that value.
"""
```

---

## PART 2: PARTICLE SWARM OPTIMIZATION (PSO) FOR RESCUE ROUTING

### Prompt 2.1: PSO Core Algorithm

```
Create a RescueOptimizer class that implements Particle Swarm Optimization.

This class should:

1. Initialize method:
   - Accept list of victims and rescue teams
   - Create population of PSO_SWARM_SIZE particles
   - Each particle represents a possible victim-to-team assignment
   - Initialize random positions and velocities

2. optimize_routes() method:
   - Main PSO loop that runs PSO_ITERATIONS
   - For each iteration:
     a) Evaluate fitness of each particle
     b) Update personal best (pbest) for each particle
     c) Update global best (gbest) across all particles
     d) Update velocity using PSO equation:
        velocity = w*velocity + c1*rand()*(pbest - position) + c2*rand()*(gbest - position)
     e) Update position: position = position + velocity
     f) Clamp velocity to reasonable bounds
   - Return best assignment found

3. evaluate_fitness() method:
   - Score how good an assignment is
   - Fitness = (speed reward) + (distance reward) - (congestion penalty) - (overload penalty)
   - Speed reward: 1000 / total_rescue_time
   - Distance reward: 1000 / total_distance
   - Congestion penalty: penalize victims waiting >15 minutes
   - Overload penalty: penalize teams with >capacity assignments
   - Higher fitness = better solution

4. compute_travel_time() method:
   - Use simple Euclidean distance / 1.0 m/s
   - Account for victim extraction time based on classification:
     * CONSCIOUS: 30 seconds
     * UNCONSCIOUS: 120 seconds
     * TRAPPED_IN_RUBBLE: 600 seconds

5. discretize_assignment() method:
   - Convert continuous PSO position to discrete team assignments
   - Use argmax to assign each victim to their highest-scoring team
   - Ensure no team exceeds capacity
   - Return dictionary {victim_id: team_id}

Include detailed comments and docstrings.
Add logging to track convergence (best fitness per iteration).
Add method to get convergence history for plotting.
```

### Prompt 2.2: PSO Visualization Helper

```
Add to RescueOptimizer:

1. get_convergence_history() method:
   - Return list of best fitness values per iteration
   - Used for plotting convergence curve

2. get_assignment_quality_metrics() method:
   - Return dictionary with:
     * total_rescue_time: sum of all rescue operations
     * avg_rescue_time: mean time per team
     * max_wait_time: worst victim waiting time
     * min_wait_time: best victim waiting time
     * team_utilization: avg load on teams
     * efficiency_score: victims_rescued / total_distance

3. visualize_assignment() method:
   - Create simple text visualization of final assignment
   - Show each team and their assigned victims in order
   - Show estimated time for each team

Add assertions to validate that:
- All victims are assigned
- No team exceeds capacity
- Total_time > 0
- All assignments are unique
```

---

## PART 3: SURFACE TENSION FLUID MODEL FOR CROWD EVACUATION

### Prompt 3.1: Potential Field & Velocity Field

```
Create a CrowdFlowOptimizer class for evacuation routing.

This class manages crowd flow simulation:

1. __init__ method:
   - Accept world dimensions, exit locations, obstacle map
   - Create potential field grid (10m x 10m cells for fast computation)
   - Initialize velocity field (same grid)
   - Store configuration parameters

2. compute_potential_field() method:
   - For each grid cell, calculate potential value
   - potential = distance_to_nearest_exit - distance_from_hazard + local_density_penalty
   - Distance to exit: 0 at exit, increases away from it
   - Distance from hazard: negative (repels), so cells near hazards have lower potential
   - Density penalty: +0.2 per person in 5m² area
   - Return 2D numpy array of potentials

3. compute_velocity_field() method:
   - For each grid cell, compute velocity direction
   - velocity_direction = -gradient_of_potential (negative = downhill toward exits)
   - Use numpy.gradient() for partial derivatives
   - Normalize to unit vectors
   - Return 2D array of velocity vectors

4. get_victim_velocity() method:
   - Query velocity at victim's position
   - Interpolate between grid cells if victim is between cells
   - Return velocity vector (vx, vy)

5. update_victim_position() method:
   - Accept victim and time_step
   - Get velocity at victim's current location
   - Apply damping: velocity *= (1.0 - VISCOSITY)
   - Update position: new_pos = pos + velocity * time_step
   - Check for collisions with obstacles
   - If collision, slide along boundary
   - Update victim.x, victim.y, victim.velocity
   - Return new position

6. detect_congestion() method:
   - Divide space into regions
   - For each region, count victims and calculate density
   - If density > TARGET_DENSITY * 1.5, flag as congested
   - Return list of congested regions

Include numpy-based computation for speed.
Add bounds checking to keep victims in simulation world.
```

### Prompt 3.2: Surface Tension Implementation

```
Add to CrowdFlowOptimizer:

1. apply_surface_tension() method:
   - For each victim, apply repulsion from nearby boundaries/obstacles
   - distance_to_boundary = minimum distance to any wall/obstacle
   - If distance < PERSONAL_SPACE:
     * tension_force = SURFACE_TENSION * (PERSONAL_SPACE - distance) / PERSONAL_SPACE
     * direction = direction_away_from_boundary
     * Modify victim velocity to include repulsion
   - This prevents victims from "piling up" at walls

2. update_surface_tension_dynamic() method:
   - Monitor crowd density continuously
   - If congestion detected in region:
     * Increase SURFACE_TENSION in that region
     * This slows people down and spreads them out
   - If region is under-utilized:
     * Decrease SURFACE_TENSION
     * This speeds movement up
   - Use exponential smoothing: tension *= 1.05 or 0.95

3. apply_herding_behavior() method:
   - At high panic, victims follow nearby people instead of optimal path
   - For each victim:
     * Find K nearest neighbors (K=3-5)
     * Calculate average direction of neighbors
     * Blend: final_direction = alpha * neighbor_direction + (1-alpha) * optimal_direction
     * alpha increases with panic level
   - At panic=0.5: 30% herding, 70% optimal
   - At panic=0.9: 80% herding, 20% optimal

4. prevent_catastrophic_failure() method:
   - Check for stampede conditions (high density + chaotic motion)
   - If density > 5.0 AND velocity_variance > 0.5:
     * Trigger emergency intervention
     * Broadcast calming messages (reduce panic)
     * Force dramatic increase in surface tension
     * Deploy imaginary rescue teams to manage crowd
     * Return True if intervention triggered, False otherwise

5. reset_potential_field() method:
   - Recompute potential field at each simulation step
   - Call this before each velocity field update
   - Allows dynamic hazards to influence flow

Include detailed comments.
Add safety checks to prevent NaN/infinity values.
Test with sample victim positions to verify reasonable behavior.
```

---

## PART 4: DYNAMIC PANIC COEFFICIENT

### Prompt 4.1: Panic Calculation

```
Create a PanicBehaviorModel class:

1. __init__ method:
   - Store configuration parameters
   - Initialize panic history for tracking

2. compute_panic_coefficient() method:
   - Accept: victim, current_hazards, time_since_event, simulation_state
   - Calculate panic based on 5 factors (each 0-1):
   
   a) Hazard Proximity Factor:
      - Find distance to nearest hazard
      - If distance < critical_radius: hazard_panic = 1.0
      - Else if distance < critical_radius * 2: hazard_panic = 0.5
      - Else if distance < critical_radius * 4: hazard_panic = 0.2
      - Else: hazard_panic = 0.0
   
   b) Crowd Density Factor:
      - Count nearby victims within 5m radius
      - If nearby_count > 20: density_panic = 0.8
      - Else if nearby_count > 10: density_panic = 0.4
      - Else: density_panic = 0.1
   
   c) Duration Factor:
      - If time < 5 minutes: apply 1.2x multiplier (acute shock)
      - If time > 30 minutes: apply 0.8x multiplier (fatigue/resignation)
      - Else: no multiplier
   
   d) Communication Factor:
      - If victim has_received_guidance: multiply panic by 0.7
      - Else: no change
   
   e) Group Cohesion Factor:
      - Count known people (same group_id) nearby
      - If nearby_known > 0: multiply panic by 0.85
      - Else: no change
   
   - Combine: panic = (0.3*hazard + 0.4*density + 0.3*other_factors)
   - Apply modifiers from factors c, d, e
   - Clamp to [0.0, 1.0]
   - Return panic_level

3. adapt_movement_behavior() method:
   - Accept: victim, panic_coefficient
   - Adjust movement speed based on panic:
     * base_speed = 1.4 m/s
     * If panic > 0.7: speed = 1.4 * (1.0 + panic * 0.6) [up to 1.84 m/s]
     * If panic > 0.4: speed = 1.4 * (1.0 + panic * 0.3)
     * Else: speed = 1.4
   - Adjust erratic motion (jitter):
     * If panic > 0.6: add random jitter to direction
   - Adjust herding (follow neighbors):
     * higher_panic → more herding
   - Return modified movement parameters

4. recovery_from_panic() method:
   - Natural panic decay over time with reassurance
   - panic_new = panic_old * PANIC_DECAY_RATE
   - If victim.has_received_guidance: decay faster (0.90 instead of 0.95)
   - If victim.assigned_rescue_team is not None: decay even faster (0.85)
   - Update victim.panic_level

Include numpy for efficient calculation.
Add validation that panic values stay in [0, 1].
Log panic statistics (mean, std dev, max) each simulation step.
```

### Prompt 4.2: Panic Monitoring & Safety

```
Add to PanicBehaviorModel:

1. monitor_for_cascading_panic() method:
   - Check if panic is spreading exponentially
   - Calculate panic correlation between nearby victims
   - If correlation > 0.8 AND mean_panic > 0.7:
     * Panic cascade detected
     * Trigger intervention: broadcast calming messages
     * Reduce all panic levels by 0.2
     * Return True
   - Return False if no cascade

2. monitor_for_freeze_response() method:
   - At extreme panic (>0.9), some victims freeze
   - For each victim with panic > 0.9:
     * 10% chance to freeze (velocity = 0)
     * Remain frozen for 2-5 seconds
     * Then gradually resume movement
   - This is realistic (fight-or-flight response)

3. get_panic_statistics() method:
   - Return dictionary with:
     * mean_panic: average across all victims
     * max_panic: worst panic level
     * min_panic: best panic level
     * std_panic: standard deviation
     * panic_above_threshold: count of victims with panic > 0.8
     * freezing_count: number of frozen victims

4. visualize_panic_distribution() method:
   - Return histogram data of panic levels
   - Used for plotting panic distribution over time

Add comprehensive comments explaining psychology.
Include assertions for all calculations.
```

---

## PART 5: SENSOR FUSION (MULTI-SOURCE DETECTION)

### Prompt 5.1: Multi-Sensor Fusion Pipeline

```
Create a SensorFusionModule class:

1. __init__ method:
   - Initialize sensor parameters (range, accuracy)
   - Create grid for clustering detections
   - Store configuration

2. simulate_radar_detection() method:
   - Accept: actual_victims, noise_level
   - For each victim within RADAR_MAX_RANGE:
     * Add position noise (Gaussian, ~2m std dev)
     * Calculate vital_sign_score based on victim state
     * Return detection with (x, y, confidence, vital_score)
   - Confidence = 1.0 - (distance / RADAR_MAX_RANGE) * noise_factor
   - VITAL_SCORE high if victim is conscious, low if unconscious
   - Return list of radar_detections

3. simulate_thermal_detection() method:
   - Accept: actual_victims, noise_level
   - For each victim within THERMAL_MAX_RANGE:
     * Detect body heat signature
     * Add temperature noise
     * Return detection with (x, y, confidence, temperature)
   - Confidence based on temperature match (32-40°C range)
   - Return list of thermal_detections

4. simulate_drone_detection() method:
   - Accept: actual_victims, noise_level
   - Drones can only see visible victims (line of sight)
   - If victim is in open area: high confidence (0.95)
   - If victim is under debris: low/no detection
   - Return list of drone_detections with (x, y, person_confidence, pose)

5. fuse_detections() method (MAIN FUSION):
   - Accept: radar_detections, thermal_detections, drone_detections
   - Create output: list of fused VictimProfiles
   - Algorithm:
     a) Grid-based clustering: divide space into 10m x 10m cells
     b) For each thermal detection:
        - Find grid cell
        - Find closest radar in same cell (within 3m)
        - If found AND confidence > threshold:
          * CREATE VICTIM PROFILE with fused data
          * Fusion confidence = MIN(radar.conf, thermal.conf)
          * Classification = CONSCIOUS/UNCONSCIOUS based on vitals
        - Store created victims with unique IDs
     c) For each drone detection:
        - Find nearby fused victim (within 5m)
        - If found: boost confidence (×1.2)
        - If NOT found AND confidence > 0.95:
          * Create new UNCONFIRMED victim (lower priority)
   - Return list of confirmed victims with confidence scores

6. remove_false_positives() method:
   - Victims not confirmed by at least 2 sensors removed
   - Victims with confidence < CONFIDENCE_THRESHOLD removed
   - Tracking: match victims across time frames
     * If victim position consistent with previous: same ID
     * If new: assign new ID

Include detailed comments on multi-sensor decision logic.
Add validation: assert all victims have confidence in [0, 1].
Log detection statistics: radar_count, thermal_count, fused_count, false_positives.
```

### Prompt 5.2: Victim Classification & Risk Scoring

```
Add to SensorFusionModule:

1. classify_victim() method:
   - Accept: radar_detection, thermal_detection
   - Classify as: CONSCIOUS, UNCONSCIOUS, TRAPPED_IN_RUBBLE, UNCERTAIN
   - Logic:
     * If vital_signs > 0.5 AND motion > 0.5: CONSCIOUS
     * Else if vital_signs > 0.3 AND motion > 0.2: UNCONSCIOUS
     * Else if under_debris detected: TRAPPED_IN_RUBBLE
     * Else: UNCERTAIN

2. compute_victim_risk_score() method:
   - Accept: victim, hazards
   - Calculate 0-1 risk score (higher = more urgent)
   - Factors:
     a) Viability (likelihood of survival):
        - CONSCIOUS: 0.95
        - UNCONSCIOUS: 0.70
        - TRAPPED: 0.40
        - UNCERTAIN: 0.50
     b) Hazard Exposure (time until critical):
        - Estimate time_to_fatal_hazard based on hazard intensity & distance
        - If time < 5 min: hazard_urgency = 1.0
        - If time < 15 min: hazard_urgency = 0.8
        - If time < 30 min: hazard_urgency = 0.6
        - Else: hazard_urgency = 0.3
     c) Accessibility (can we reach them?):
        - If in open: 0.95
        - If under debris: 0.3
        - If underground: 0.1
   - Combine: risk = (0.3*viability + 0.5*hazard + 0.2*accessibility)
   - Return risk_score (0-1)

3. update_victim_map() method:
   - Accept: all detections
   - For each fused detection:
     * Compute risk score
     * Create/update victim profile
     * Assign initial risk_score
   - Remove stale victims (not detected for >5 seconds)
   - Track victims over time (trajectory, velocity)
   - Return updated VictimMap

Include classification confidence scoring.
Add logging of detection quality metrics.
Test with synthetic data to verify reasonable risk scores.
```

---

## PART 6: MAIN SIMULATION LOOP

### Prompt 6.1: Core Simulation Engine

```
Create a DisasterSimulation class:

1. __init__ method:
   - Accept: initial_victims, initial_teams, initial_hazards, duration
   - Initialize all components:
     * optimizer = RescueOptimizer()
     * crowd_flow = CrowdFlowOptimizer()
     * panic_model = PanicBehaviorModel()
     * sensor_fusion = SensorFusionModule()
   - Create state: SimulationState
   - Initialize metrics tracking (lists for plotting)

2. run_simulation() method:
   - Main loop that runs for SIMULATION_DURATION
   - Timestep = 1.0 / UPDATE_FREQUENCY (0.5 seconds)
   - Each iteration:
     a) Update hazard spread (if applicable)
     b) Simulate sensor detections (radar, thermal, drone)
     c) Fuse detections into victim map
     d) Run PSO optimization to get rescue assignments
     e) Update rescue team routes based on assignments
     f) Compute panic levels for all victims
     g) Update victim velocities using surface tension fluid model
     h) Apply herding behavior based on panic
     i) Update victim positions
     j) Check for congestion and prevent stampedes
     k) Track metrics (time, efficiency, casualties, panic)
     l) Print progress to console
     m) Store state for visualization
   - Return final SimulationState

3. update_hazards() method:
   - For each hazard:
     * Expand hazard radius if spreading
     * Update intensity
     * Remove if hazard dissipated

4. step_optimization() method:
   - Call optimizer.optimize_routes() with current victims & teams
   - Get back best assignment
   - Update team assignments
   - Return metrics

5. step_crowd_dynamics() method:
   - For each victim:
     a) Compute panic coefficient
     b) Adapt movement behavior
     c) Get velocity from potential field
     d) Update position using surface tension model
     e) Check collision with obstacles
   - Monitor for congestion
   - Return movement metrics

6. track_metrics() method:
   - Compute each timestep:
     * total_victims_detected
     * total_evacuated (reached safe zone)
     * total_rescued (by teams)
     * avg_panic_level
     * max_wait_time
     * total_distance_traveled
     * team_utilization
   - Store in metrics dictionary
   - Print progress: "T=50s: Detected=123, Evacuated=45, Rescued=12, AvgPanic=0.62"

Include detailed docstrings.
Add assertions to validate state consistency.
Save intermediate states for visualization.
```

### Prompt 6.2: Simulation Utilities & Output

```
Add to DisasterSimulation:

1. get_metrics_summary() method:
   - Return dictionary with final metrics:
     * total_rescue_time
     * total_evacuation_time
     * total_casualties (from stampedes/hazards)
     * avg_panic_level
     * optimization_efficiency
     * pso_convergence_history
     * crowd_flow_efficiency

2. print_final_report() method:
   - Print comprehensive summary:
     * Total victims: N
     * Successfully evacuated: N (X%)
     * Successfully rescued: N (X%)
     * Casualties: N (X%)
     * Average waiting time: T seconds
     * Average rescue time: T seconds
     * Peak panic level: X.XX
     * Final panic level: X.XX
     * PSO convergence: plot ASCII graph
     * Team utilization: X%

3. save_simulation_data() method:
   - Save all state history to JSON file
   - For each timestep: victims, teams, hazards, metrics
   - Used for offline analysis and detailed visualization

4. validate_simulation_state() method:
   - Check invariants:
     * No duplicate victims
     * All team assignments valid
     * Metrics are non-negative
     * Panic values in [0, 1]
     * Positions within world bounds
   - Raise exception if invalid

Include error handling.
Add timing to measure simulation performance.
Create clean formatted console output.
```

---

## PART 7: VISUALIZATION & PLOTTING

### Prompt 7.1: Real-Time Animation

```
Create a SimulationVisualizer class using matplotlib:

1. __init__ method:
   - Accept: simulation state history
   - Create figure with subplots:
     * Main plot (2D world): victims, teams, hazards
     * Right side plots:
       - Panic level distribution (histogram)
       - Victim count over time (line chart)
       - PSO fitness convergence (line chart)
       - Team utilization (bar chart)

2. animate() method:
   - Create animation function using FuncAnimation
   - For each timestep:
     a) Clear main plot
     b) Draw world boundaries
     c) Draw hazard zones (red circles)
     d) Draw obstacles (if any)
     e) Draw victims as colored dots:
        - Color = panic level (green=calm, red=panicked)
        - Size = risk score (bigger = more urgent)
        - Marker: circle=unassigned, square=assigned to team, X=reached safety
     f) Draw rescue teams as blue squares
     g) Draw lines from teams to assigned victims
     h) Draw exits as green stars
     i) Add annotations: time, victim count, casualty count, avg panic
     j) Update side plots with current data

3. show() method:
   - Display animation with matplotlib
   - Set refresh rate to match simulation updates (2 Hz)
   - Add pause/play controls

4. save_animation() method:
   - Save as MP4 video file using FFmpeg
   - For presentations

Include proper legends and colorbars.
Use subplots for multiple simultaneous views.
Add time display and event markers.
```

### Prompt 7.2: Performance Plots

```
Create plotting methods:

1. plot_convergence() method:
   - Plot PSO fitness over iterations
   - X-axis: iteration number
   - Y-axis: best fitness found
   - Shows algorithm convergence

2. plot_victim_count_timeline() method:
   - Plot 3 lines:
     * Total detected victims
     * Evacuated victims
     * Rescued victims
   - X-axis: time (seconds)
   - Y-axis: count

3. plot_panic_distribution() method:
   - Histogram of panic levels over time
   - Show distribution at key timepoints (0s, 300s, 600s)
   - Highlight critical panic levels (>0.8)

4. plot_team_utilization() method:
   - Bar chart of each team's workload
   - Show: assigned victims, total time, rescues completed

5. plot_metrics_summary() method:
   - Create comprehensive dashboard:
     * Total victims / detected / evacuated / rescued / casualties
     * Average and max panic levels
     * PSO efficiency
     * Crowd flow efficiency
   - All in one figure for easy comparison

6. compare_with_baseline() method:
   - If baseline data available, compare metrics
   - Show RS-SSTO vs traditional (manual dispatch)
   - Plot improvement percentages

Include error bars where applicable.
Use professional matplotlib styling.
Add titles and axis labels.
Save all plots to PNG files.
```

---

## PART 8: MAIN ENTRY POINT & SCENARIOS

### Prompt 8.1: Scenario Generator

```
Create a ScenarioBuilder class:

1. create_office_building_scenario() method:
   - Simulate 30-story office tower
   - 4000 people evacuating from fire
   - Fire on floors 15-20, spreading upward
   - Return: initial_victims, hazards, exits

2. create_earthquake_scenario() method:
   - Simulate building collapse
   - 200 victims trapped in rubble
   - Multiple collapse zones
   - Limited accessibility
   - Return: initial_victims, hazards, exits

3. create_high_rise_fire_scenario() method:
   - 50-story hotel
   - 3000 people
   - Fire in parking garage spreading to main lobby
   - 4 stairwells available
   - Return: initial_victims, hazards, exits

4. create_concert_venue_scenario() method:
   - 10,000 people in stadium
   - Partial structural collapse
   - Multiple exits
   - Extreme panic
   - Return: initial_victims, hazards, exits

Each method should:
- Create realistic victim distribution
- Add hazard zones with spreading behavior
- Define exit locations and accessibility
- Return complete scenario data

Include comments explaining realistic parameters.
```

### Prompt 8.2: Main Execution

```
Create main.py with execution flow:

if __name__ == "__main__":
    
    # Step 1: Choose scenario
    print("Available scenarios:")
    print("1. Office Building Fire")
    print("2. Earthquake Rescue")
    print("3. High-Rise Fire")
    print("4. Concert Venue Collapse")
    
    choice = input("Select scenario (1-4): ")
    
    # Step 2: Load scenario
    builder = ScenarioBuilder()
    if choice == "1":
        victims, hazards, exits, teams = builder.create_office_building_scenario()
    elif choice == "2":
        victims, hazards, exits, teams = builder.create_earthquake_scenario()
    elif choice == "3":
        victims, hazards, exits, teams = builder.create_high_rise_fire_scenario()
    elif choice == "4":
        victims, hazards, exits, teams = builder.create_concert_venue_scenario()
    
    # Step 3: Run simulation
    print(f"\\nInitializing simulation...")
    print(f"Victims: {len(victims)}")
    print(f"Rescue Teams: {len(teams)}")
    print(f"Duration: {config.SIMULATION_DURATION} seconds\\n")
    
    sim = DisasterSimulation(victims, hazards, exits, teams, duration=config.SIMULATION_DURATION)
    final_state = sim.run_simulation()
    
    # Step 4: Display results
    sim.print_final_report()
    
    # Step 5: Visualize
    print("\\nGenerating visualization...")
    visualizer = SimulationVisualizer(sim.state_history)
    visualizer.show()
    
    # Step 6: Save data
    print("Saving simulation data...")
    sim.save_simulation_data("simulation_results.json")
    visualizer.save_animation("simulation.mp4")
    visualizer.plot_convergence()
    visualizer.plot_victim_count_timeline()
    visualizer.plot_panic_distribution()
    visualizer.print("\\nSimulation complete! Results saved.")

Add error handling for invalid input.
Add progress indicators.
Make sure console output is clean and professional.
```

---

## PART 9: INTEGRATION & TESTING

### Prompt 9.1: Unit Tests

```
Create test_algorithms.py with test cases:

1. test_pso_convergence():
   - Run PSO on small problem (20 victims, 5 teams)
   - Assert fitness improves each iteration
   - Assert final solution is valid

2. test_surface_tension():
   - Place victims in confined space
   - Run fluid model
   - Assert victims spread out (not pile up)
   - Assert victims move toward exits

3. test_panic_calculation():
   - Create victim near hazard
   - Assert panic > 0.7
   - Create victim in crowd
   - Assert panic > 0.4
   - Assert panic decays over time

4. test_sensor_fusion():
   - Create ground truth victims
   - Simulate detections with noise
   - Assert fused detections match ground truth (>90%)

5. test_simulation_invariants():
   - Run full simulation
   - Assert no victims are lost
   - Assert all metrics valid
   - Assert no crashes

Use pytest framework.
Include assertions for all critical properties.
Add timing tests (optimization should be <2s).
```

### Prompt 9.2: Integration & Validation

```
Create validation.py:

1. validate_against_baseline():
   - Compare RS-SSTO results vs traditional dispatch baseline
   - Assert RS-SSTO is 30%+ faster
   - Assert RS-SSTO has <50% casualties of baseline

2. validate_algorithm_parameters():
   - Check that parameters are in reasonable ranges
   - PSO inertia should be 0.4-0.9
   - Surface tension should be 0.1-1.0
   - Panic decay should be 0.85-0.99
   - Raise exception if invalid

3. benchmark_performance():
   - Measure simulation speed (should be >10x real-time on modern CPU)
   - Measure optimization latency (should be <2s)
   - Measure memory usage
   - Print performance report

4. sensitivity_analysis():
   - Run simulations with parameter variations
   - Test: ±10% changes to each parameter
   - Measure impact on outcomes
   - Identify most sensitive parameters

Add all validation to simulation output.
Create comprehensive reports.
```

---

## SUMMARY: Complete Copilot Workflow

After running all these prompts in order in VS Code Copilot, you'll have:

**Complete Simulation Features:**
✅ Particle Swarm Optimization for rescue team assignment
✅ Surface Tension Fluid Model for crowd evacuation  
✅ Dynamic Panic Coefficient with psychological grounding
✅ Multi-sensor fusion (radar + thermal + drone)
✅ Real-time optimization loop (<500ms latency)
✅ 4 realistic disaster scenarios
✅ Real-time 2D animation with matplotlib
✅ Comprehensive metrics tracking and reporting
✅ Unit tests and validation

**Output:**
- Animated video of disaster unfolding
- Real-time visualization of algorithm decisions
- Performance metrics showing RS-SSTO vs baseline
- Convergence plots, panic distribution, team utilization charts
- Console report with final statistics

**File Structure:**
```
rs_ssto_simulation/
├── config.py                 # All parameters
├── data_structures.py        # Victim, Team, Hazard classes
├── pso_optimizer.py          # Particle swarm optimization
├── crowd_flow.py             # Surface tension fluid model
├── panic_model.py            # Dynamic panic coefficient
├── sensor_fusion.py          # Multi-sensor detection
├── simulation.py             # Main simulation engine
├── visualizer.py             # Matplotlib animation & plots
├── scenarios.py              # Disaster scenarios
├── validation.py             # Testing & benchmarking
├── main.py                   # Entry point
└── requirements.txt          # numpy, matplotlib, etc.
```

**Next Steps:**
1. Copy each prompt into VS Code Copilot (one at a time)
2. Let Copilot generate the code
3. Review and approve each section
4. Combine all files into project
5. Run: `python main.py` and select a scenario
6. Watch the simulation animate in real-time!

---

## BONUS: Advanced Extensions (After Core Works)

Once the simulation works, you can add:

1. Real 3D visualization (using Pygame or Three.js)
2. Network effects (teams communicate, share information)
3. Equipment management (limited resources, medical supplies)
4. Environmental effects (wind for fire/smoke, rainfall for floods)
5. Realistic pathfinding (A* through obstacles)
6. Multi-floor buildings (3D coordinates)
7. REST API (run simulations via HTTP)
8. Parameter tuning optimization (meta-optimization: find best parameters)
9. Machine learning (train neural net on simulation data, then compare to PSO)
10. GIS integration (real maps, real city coordinates)

Good luck! 🚀
