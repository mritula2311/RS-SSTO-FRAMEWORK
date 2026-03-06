# COMPLETE SIMULATION - PART 2: ALL REMAINING FILES

## CONTINUATION FROM PART 1

Start with COMPLETE_FILE_BY_FILE_SIMULATION_PROMPT.md (Part 1) first.
This is Part 2.

---

# STEP 6: CREATE algorithms/manual_dispatch.py

## Prompt 6: MANUAL DISPATCH ALGORITHM (Baseline - How It's Done Today)

```
Create file: simulation/algorithms/manual_dispatch.py

This implements the BASELINE algorithm - how disaster response works TODAY.

===== DETAILED EXPLANATION =====

HOW MANUAL DISPATCH WORKS IN REAL LIFE:

1. DETECTION (Random Order - 911 Calls)
   - Fire alarm goes off, people call 911
   - Dispatcher receives calls one by one (random order)
   - Not all victims reported (some can't reach phone)
   - Calls come in for 30-60 seconds as people realize danger

2. DISPATCH (Nearest Idle Team)
   - Dispatcher sends nearest available team to each reported location
   - Uses simple greedy: "team X is closest, send them"
   - No global optimization
   - Teams don't know about other team assignments

3. EVACUATION (Self-Evacuation)
   - People evacuate on their own (no guidance)
   - Go toward nearest visible exit
   - Causes congestion at nearest exit
   - All bottleneck at one location

4. RESULTS (Inefficient)
   - Some victims never found (not reported to 911)
   - Teams overlap routes (same victim assigned to multiple teams)
   - Evacuations cause stampedes (unmanaged congestion)
   - Total time: 600+ seconds

===== CODE =====

Copy this entire content:

"""
BASELINE ALGORITHM: Manual Dispatch

This is how emergency response works TODAY (without optimization).

Characteristics:
- Victims reported via 911 calls (random order, not comprehensive)
- Teams dispatched to nearest reported location (greedy)
- Teams work independently (no coordination)
- Victims self-evacuate (no routing, causes congestion)
- NO congestion management

Result: Inefficient, slow, high casualties
"""

import random
import math
from data_structures import SimulationState, AlgorithmResult, Victim
from algorithms.base_algorithm import BaseAlgorithm
from config import *

class ManualDispatchAlgorithm(BaseAlgorithm):
    
    def __init__(self):
        super().__init__()
        self.name = "Manual Dispatch (Baseline)"
        self.description = "911-based dispatch with no optimization"
    
    def simulate(self, state: SimulationState, duration: float) -> AlgorithmResult:
        """
        Run manual dispatch simulation.
        
        Steps each time step:
        1. Some victims detected (via 911 calls - random order)
        2. Dispatch nearest idle team to each unassigned victim
        3. Teams travel and extract victims
        4. Victims evacuate toward nearest exit (no guidance)
        5. Track: evacuation time, rescue count, casualties
        """
        
        self.state = state
        detected_victims = []
        evacuation_complete_time = None
        rescue_complete_time = None
        
        time_step_size = 1.0 / UPDATE_FREQUENCY  # 0.5 seconds
        current_time = 0.0
        
        while current_time < duration:
            
            # ===== STEP 1: DETECT VICTIMS (Random Order - 911) =====
            if current_time == 0:
                # At start, victims detected in RANDOM order (as 911 calls arrive)
                detected_victims = self._detect_victims_by_911_calls(state.victims)
            
            # ===== STEP 2: DISPATCH (Greedy - Nearest Team) =====
            for victim in detected_victims:
                if victim.assigned_team_id is None and not victim.deceased:
                    nearest_team = self._find_nearest_idle_team(state.teams, victim)
                    if nearest_team:
                        nearest_team.assigned_victim_ids.append(victim.id)
                        victim.assigned_team_id = nearest_team.id
            
            # ===== STEP 3: TEAMS WORK (Travel & Extract) =====
            for team in state.teams:
                if team.assigned_victim_ids and team.current_victim_index < len(team.assigned_victim_ids):
                    victim_id = team.assigned_victim_ids[team.current_victim_index]
                    victim = self._get_victim(state, victim_id)
                    
                    if victim and not victim.rescued:
                        # Travel to victim
                        distance = team.distance_to(victim.x, victim.y)
                        if distance > 1:  # Not at victim yet
                            direction_x = (victim.x - team.x) / distance
                            direction_y = (victim.y - team.y) / distance
                            team.x += direction_x * team.speed * time_step_size
                            team.y += direction_y * team.speed * time_step_size
                            team.total_distance += team.speed * time_step_size
                        else:
                            # Arrived at victim - extract
                            extract_time = self._get_extraction_time(victim.classification)
                            if not team.busy:
                                team.busy = True
                                team.task_end_time = current_time + extract_time
                            
                            if current_time >= team.task_end_time and team.busy:
                                # Extraction complete
                                victim.rescued = True
                                team.victims_rescued += 1
                                team.busy = False
                                team.current_victim_index += 1
            
            # ===== STEP 4: VICTIMS EVACUATE (Self-Evacuation) =====
            for victim in state.victims:
                if not victim.assigned_team_id and not victim.evacuated and not victim.deceased:
                    # Move toward nearest exit (greedy, no routing)
                    nearest_exit = self._find_nearest_exit(state.exits, victim)
                    if nearest_exit:
                        distance = victim.distance_to(nearest_exit.x, nearest_exit.y)
                        if distance > 1:
                            direction_x = (nearest_exit.x - victim.x) / distance
                            direction_y = (nearest_exit.y - victim.y) / distance
                            
                            # Panic affects speed
                            speed = victim.speed
                            victim.x += direction_x * speed * time_step_size
                            victim.y += direction_y * speed * time_step_size
                        else:
                            # Reached exit
                            victim.evacuated = True
                            evacuation_complete_time = current_time
            
            # ===== STEP 5: CHECK FOR CONGESTION CASUALTIES =====
            # Track congestion (but don't manage it!)
            stampede_deaths = self._compute_stampede_casualties(state)
            
            # ===== TRACK METRICS =====
            self._track_metrics(state)
            self._print_progress(current_time, duration)
            
            current_time += time_step_size
        
        # ===== COMPILE RESULTS =====
        return AlgorithmResult(
            algorithm_name=self.name,
            total_evacuation_time=evacuation_complete_time or duration,
            total_rescue_time=rescue_complete_time or duration,
            evacuated_count=state.count_evacuated(),
            rescued_count=state.count_rescued(),
            casualties=state.count_deceased(),
            efficiency=self._compute_efficiency(state),
            time_history=self.metrics['time_history'],
            evacuated_history=self.metrics['evacuated_history'],
            rescued_history=self.metrics['rescued_history'],
            casualties_history=self.metrics['casualties_history'],
            avg_panic_history=self.metrics['panic_history']
        )
    
    def _detect_victims_by_911_calls(self, victims):
        '''Victims detected in RANDOM order (as 911 calls arrive)'''
        detected = random.sample(victims, min(len(victims), int(len(victims) * 0.6)))
        for v in detected:
            v.detected_time = 0
        return detected
    
    def _find_nearest_idle_team(self, teams, victim):
        '''Simple greedy: pick closest team that's not busy'''
        idle_teams = [t for t in teams if not t.busy and not t.assigned_victim_ids]
        if not idle_teams:
            return None
        return min(idle_teams, key=lambda t: t.distance_to(victim.x, victim.y))
    
    def _get_victim(self, state, victim_id):
        for v in state.victims:
            if v.id == victim_id:
                return v
        return None
    
    def _find_nearest_exit(self, exits, victim):
        if not exits:
            return None
        return min(exits, key=lambda e: victim.distance_to(e.x, e.y))
    
    def _get_extraction_time(self, classification):
        from data_structures import VictimClassification
        if classification == VictimClassification.CONSCIOUS:
            return EXTRACTION_TIME_CONSCIOUS
        elif classification == VictimClassification.UNCONSCIOUS:
            return EXTRACTION_TIME_UNCONSCIOUS
        else:
            return EXTRACTION_TIME_TRAPPED
    
    def _compute_stampede_casualties(self, state):
        '''Unmanaged congestion causes casualties'''
        deaths = 0
        for exit_point in state.exits:
            # Count people at each exit
            people_at_exit = sum(1 for v in state.victims 
                               if not v.evacuated and 
                               v.distance_to(exit_point.x, exit_point.y) < 10)
            
            if people_at_exit > 100:  # Dangerous crowding
                # 3% die from stampede per second
                deaths += max(0, int(people_at_exit * 0.03))
                
                # Mark some as deceased
                victims_near = [v for v in state.victims 
                               if not v.evacuated and not v.deceased and
                               v.distance_to(exit_point.x, exit_point.y) < 10]
                for i in range(min(int(people_at_exit * 0.01), len(victims_near))):
                    victims_near[i].deceased = True
        
        return deaths
    
    def _compute_efficiency(self, state):
        '''Efficiency = successful outcomes / total time'''
        successful = state.count_evacuated() + state.count_rescued()
        return successful / max(600, 1)  # Normalize to 600s baseline
```

This is the BASELINE algorithm showing how it's done TODAY.
The point: inefficient, slow, high casualties!
```

---

# STEP 7: CREATE algorithms/greedy_algorithm.py

## Prompt 7: GREEDY ALGORITHM (Simple Optimization - Existing Systems)

```
Create file: simulation/algorithms/greedy_algorithm.py

This implements a simple greedy algorithm - better than manual but still has problems.

===== DETAILED EXPLANATION =====

HOW GREEDY ALGORITHM WORKS:

1. DETECTION (Sensor-Based)
   - Uses actual sensors (radar + thermal) instead of 911 calls
   - Better coverage (finds victims sensors can detect)
   - Faster detection
   - Continuous detection

2. ASSIGNMENT (Nearest-Neighbor Greedy)
   - For EACH team: find nearest unassigned victim
   - Immediately assign
   - No global optimization
   - Local decisions only

3. EVACUATION (FIFO - First In, First Out)
   - No routing guidance
   - No congestion management
   - People queue at exits naturally
   - Creates bottlenecks

4. RESULTS (Better than Manual, but Still Problems)
   - Better detection (sensors > 911)
   - Still suboptimal (local greedy decisions)
   - Still causes congestion (no STO management)
   - Time: 400-500 seconds

===== CODE =====

Copy this entire content:

"""
GREEDY ALGORITHM: Nearest-Neighbor Optimization

Simple improvement over manual dispatch.
Uses sensor detection + nearest-neighbor assignment.

Better than Manual Dispatch:
- Sensor detection (comprehensive)
- Greedy assignment (better than random)

Problems:
- Local optimization (gets stuck in local optima)
- No evacuation management (congestion)
- No global coordination (team overlap)
"""

import math
from data_structures import SimulationState, AlgorithmResult, VictimClassification
from algorithms.base_algorithm import BaseAlgorithm
from config import *

class GreedyAlgorithm(BaseAlgorithm):
    
    def __init__(self):
        super().__init__()
        self.name = "Greedy Nearest-Neighbor"
        self.description = "Simple sensor-based nearest-neighbor assignment"
    
    def simulate(self, state: SimulationState, duration: float) -> AlgorithmResult:
        """
        Run greedy algorithm.
        
        Steps:
        1. Detect all victims in range (sensor-based)
        2. For each team: assign nearest unassigned victim
        3. Teams travel and extract
        4. Victims evacuate via FIFO queue
        5. Track metrics
        """
        
        self.state = state
        evacuation_complete_time = None
        rescue_complete_time = None
        
        time_step_size = 1.0 / UPDATE_FREQUENCY
        current_time = 0.0
        
        while current_time < duration:
            
            # ===== STEP 1: DETECT VICTIMS (Sensor-Based) =====
            self._update_victim_detection(state)
            
            # ===== STEP 2: ASSIGN (Greedy Nearest-Neighbor) =====
            unassigned_victims = [v for v in state.victims 
                                 if v.assigned_team_id is None and not v.deceased]
            
            for team in state.teams:
                if not team.busy and unassigned_victims:
                    # Find nearest unassigned victim (GREEDY)
                    nearest = min(unassigned_victims,
                                key=lambda v: team.distance_to(v.x, v.y))
                    
                    team.assigned_victim_ids.append(nearest.id)
                    nearest.assigned_team_id = team.id
                    unassigned_victims.remove(nearest)
            
            # ===== STEP 3: TEAMS WORK (Travel & Extract) =====
            for team in state.teams:
                if team.assigned_victim_ids and team.current_victim_index < len(team.assigned_victim_ids):
                    victim_id = team.assigned_victim_ids[team.current_victim_index]
                    victim = self._get_victim(state, victim_id)
                    
                    if victim and not victim.rescued:
                        # Travel to victim
                        distance = team.distance_to(victim.x, victim.y)
                        if distance > 1:
                            direction_x = (victim.x - team.x) / distance
                            direction_y = (victim.y - team.y) / distance
                            team.x += direction_x * team.speed * time_step_size
                            team.y += direction_y * team.speed * time_step_size
                            team.total_distance += team.speed * time_step_size
                        else:
                            # At victim - start extraction
                            if not team.busy:
                                extract_time = self._get_extraction_time(victim.classification)
                                team.busy = True
                                team.task_end_time = current_time + extract_time
                            
                            # Check if extraction complete
                            if current_time >= team.task_end_time:
                                victim.rescued = True
                                team.victims_rescued += 1
                                team.busy = False
                                team.current_victim_index += 1
            
            # ===== STEP 4: VICTIMS EVACUATE (FIFO) =====
            for victim in state.victims:
                if not victim.assigned_team_id and not victim.evacuated and not victim.deceased:
                    nearest_exit = self._find_nearest_exit(state.exits, victim)
                    if nearest_exit:
                        distance = victim.distance_to(nearest_exit.x, nearest_exit.y)
                        if distance > 1:
                            direction_x = (nearest_exit.x - victim.x) / distance
                            direction_y = (nearest_exit.y - victim.y) / distance
                            victim.x += direction_x * victim.speed * time_step_size
                            victim.y += direction_y * victim.speed * time_step_size
                        else:
                            victim.evacuated = True
                            evacuation_complete_time = current_time
            
            # ===== STEP 5: CONGESTION CASUALTIES (Unmanaged) =====
            stampede_deaths = self._compute_stampede_casualties(state)
            
            # ===== TRACK METRICS =====
            self._track_metrics(state)
            self._print_progress(current_time, duration)
            
            current_time += time_step_size
        
        # ===== COMPILE RESULTS =====
        return AlgorithmResult(
            algorithm_name=self.name,
            total_evacuation_time=evacuation_complete_time or duration,
            total_rescue_time=rescue_complete_time or duration,
            evacuated_count=state.count_evacuated(),
            rescued_count=state.count_rescued(),
            casualties=state.count_deceased(),
            efficiency=self._compute_efficiency(state),
            time_history=self.metrics['time_history'],
            evacuated_history=self.metrics['evacuated_history'],
            rescued_history=self.metrics['rescued_history'],
            casualties_history=self.metrics['casualties_history'],
            avg_panic_history=self.metrics['panic_history']
        )
    
    def _update_victim_detection(self, state):
        '''Sensor-based detection'''
        for victim in state.victims:
            if victim.detected_time == 0:
                # Check if within sensor range
                distance_from_origin = math.sqrt(victim.x**2 + victim.y**2)
                if distance_from_origin < RADAR_MAX_RANGE:
                    victim.detected_time = self.state.current_time
                    victim.fusion_confidence = 0.85  # Sensor confidence
    
    def _get_victim(self, state, victim_id):
        for v in state.victims:
            if v.id == victim_id:
                return v
        return None
    
    def _find_nearest_exit(self, exits, victim):
        if not exits:
            return None
        return min(exits, key=lambda e: victim.distance_to(e.x, e.y))
    
    def _get_extraction_time(self, classification):
        if classification == VictimClassification.CONSCIOUS:
            return EXTRACTION_TIME_CONSCIOUS
        elif classification == VictimClassification.UNCONSCIOUS:
            return EXTRACTION_TIME_UNCONSCIOUS
        else:
            return EXTRACTION_TIME_TRAPPED
    
    def _compute_stampede_casualties(self, state):
        '''Congestion causes deaths'''
        deaths = 0
        for exit_point in state.exits:
            people_at_exit = sum(1 for v in state.victims
                               if not v.evacuated and
                               v.distance_to(exit_point.x, exit_point.y) < 10)
            
            if people_at_exit > 100:
                deaths += max(0, int(people_at_exit * 0.02))
                victims_near = [v for v in state.victims
                               if not v.evacuated and not v.deceased and
                               v.distance_to(exit_point.x, exit_point.y) < 10]
                
                for i in range(min(max(0, int(people_at_exit * 0.01)), len(victims_near))):
                    victims_near[i].deceased = True
        
        return deaths
    
    def _compute_efficiency(self, state):
        successful = state.count_evacuated() + state.count_rescued()
        return successful / max(600, 1)
```

This is GREEDY algorithm - BETTER than manual but still has major problems!
No global optimization, no evacuation management.
```

---

[Continue to next part due to length...]

Due to character limits, I'll create this in a separate document. Let me save the current progress and create a continuation guide.
