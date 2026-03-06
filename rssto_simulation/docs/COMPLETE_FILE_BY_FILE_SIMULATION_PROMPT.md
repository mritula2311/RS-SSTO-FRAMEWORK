# COMPLETE SIMULATION PROJECT - FILE-BY-FILE DETAILED PROMPT

## MASTER GUIDE: Every File You Need to Create

Follow this guide in exact order. Each section is a complete prompt to copy into VS Code Copilot.

---

# FOLDER STRUCTURE TO CREATE

```
Create a folder called "simulation" in VS Code, then create this structure:

simulation/
├── config.py                          # ALL configuration parameters
├── data_structures.py                 # Victim, Team, Hazard classes
├── algorithms/
│   ├── __init__.py
│   ├── base_algorithm.py              # Base class for all algorithms
│   ├── manual_dispatch.py             # Baseline: manual dispatch (911)
│   ├── greedy_algorithm.py            # Existing: greedy nearest-neighbor
│   └── rs_ssto_algorithm.py           # Proposed: PSO + Surface Tension
├── core/
│   ├── __init__.py
│   ├── sensor_fusion.py               # Multi-sensor detection fusion
│   ├── panic_model.py                 # Dynamic panic coefficient
│   ├── pso_optimizer.py               # Particle swarm optimization
│   ├── sto_manager.py                 # Surface tension optimization
│   └── physics_engine.py              # Physics calculations
├── utils/
│   ├── __init__.py
│   ├── distance_calc.py               # Distance & pathfinding
│   └── helpers.py                     # Helper functions
├── scenarios/
│   ├── __init__.py
│   └── building_fire.py               # Building fire scenario (4000 people)
├── visualization/
│   ├── __init__.py
│   ├── live_animator.py               # Real-time 2D animation
│   ├── plot_generator.py              # Generate plots
│   └── comparison_visualizer.py       # Side-by-side algorithm comparison
├── simulation_engine.py               # Main simulation loop (handles one algorithm)
├── comparison_runner.py               # Run all 3 algorithms side-by-side
├── main.py                            # Entry point - choose what to run
└── requirements.txt                   # Python dependencies
```

Follow the prompts below IN ORDER to create each file.

---

# STEP 1: CREATE requirements.txt

## Prompt 1: Requirements File

```
Create a file named requirements.txt in the simulation folder.

This file specifies all Python packages needed.

Just copy this content exactly:

numpy==1.24.3
matplotlib==3.7.1
pandas==2.0.2
scipy==1.11.0
pillow==10.0.0

After file is created, install with: pip install -r requirements.txt
```

---

# STEP 2: CREATE config.py

## Prompt 2: Configuration File - COMPLETE VERSION

```
Create file: simulation/config.py

THIS IS YOUR "KNOB-TURNING" FILE. Every parameter that can be tuned goes here.
Copy the entire content below:

"""
RS-SSTO SIMULATION - GLOBAL CONFIGURATION

This file contains ALL parameters used in the simulation.
Modify values here to change algorithm behavior, scenario difficulty, etc.
DO NOT hard-code numbers in other files - reference config.py instead.
"""

# ============================================================================
# SIMULATION CORE PARAMETERS
# ============================================================================

SIMULATION_DURATION = 600  # Total seconds to simulate (10 minutes)
UPDATE_FREQUENCY = 2.0  # Updates per second (every 0.5 seconds)
TIME_STEP = 1.0 / UPDATE_FREQUENCY  # 0.5 seconds

WORLD_WIDTH = 500  # Simulation world size (meters)
WORLD_HEIGHT = 500

# ============================================================================
# VICTIM PARAMETERS  
# ============================================================================

INITIAL_VICTIMS = 4000  # Normal people (can self-evacuate)
INITIAL_TRAPPED = 15    # Need rescue team extraction

VICTIM_BASE_SPEED = 1.4  # Normal walking speed (m/s)
VICTIM_MAX_SPEED = 1.84  # Maximum speed when panicked
VICTIM_MIN_SPEED = 0.7   # Minimum speed (freeze state)

# ============================================================================
# RESCUE TEAM PARAMETERS
# ============================================================================

NUM_RESCUE_TEAMS = 15       # Total teams available
TEAM_SPEED = 1.0            # m/s (with equipment)
TEAM_CAPACITY = 3           # Max victims per team

# How long to extract each victim type
EXTRACTION_TIME_CONSCIOUS = 30      # seconds (can walk)
EXTRACTION_TIME_UNCONSCIOUS = 120   # seconds (stretcher)
EXTRACTION_TIME_TRAPPED = 600       # seconds (under rubble, 10 minutes!)

# ============================================================================
# PARTICLE SWARM OPTIMIZATION (PSO) - For Rescue Assignment
# ============================================================================

PSO_SWARM_SIZE = 50         # Number of particles
PSO_ITERATIONS = 100        # Iterations per optimization cycle
PSO_INERTIA = 0.7           # Balance: exploration vs exploitation
PSO_COGNITIVE = 1.5         # Personal best weight
PSO_SOCIAL = 1.5            # Global best weight
PSO_UPDATE_FREQUENCY = 0.5  # Run optimization every 500ms

# ============================================================================
# SURFACE TENSION OPTIMIZATION (STO) - For Evacuation Flow
# ============================================================================

SURFACE_TENSION = 0.5       # Base repulsion strength (tune 0.1-1.0)
VISCOSITY = 0.2             # Flow resistance (crowd thickness)
PERSONAL_SPACE = 1.5        # Distance from boundaries (meters)
VELOCITY_DAMPING = 0.95     # Friction coefficient

# Crowd density thresholds
TARGET_DENSITY = 2.0        # Ideal people per m²
WARNING_DENSITY = 3.0       # High but manageable
CRITICAL_DENSITY = 5.0      # Crush/stampede risk
CRUSH_DENSITY = 7.0         # Immediate danger

# Grid for field computation
POTENTIAL_GRID_SIZE = 10    # meters per grid cell

# ============================================================================
# PANIC COEFFICIENT - For Behavioral Adaptation
# ============================================================================

# What factors influence panic (weights)
PANIC_HAZARD_WEIGHT = 0.6      # Hazard proximity effect
PANIC_DENSITY_WEIGHT = 0.4     # Crowd density effect

# Time-based modifiers
PANIC_TIME_EARLY_MULTIPLIER = 1.2   # First 5 minutes (acute shock)
PANIC_TIME_LATE_MULTIPLIER = 0.8    # After 30 minutes (fatigue)

# Recovery rates
PANIC_DECAY_RATE = 0.95                    # Natural decay per second
PANIC_DECAY_WITH_GUIDANCE = 0.90           # If receiving system guidance
PANIC_DECAY_WITH_FAMILY = 0.85             # If with group/family

# Panic levels
PANIC_LOW = 0.3         # Calm
PANIC_MEDIUM = 0.6      # Stressed
PANIC_HIGH = 0.8        # Panicked
PANIC_CRITICAL = 0.9    # May freeze or act dangerously

# ============================================================================
# SENSOR FUSION PARAMETERS
# ============================================================================

# Detection ranges
RADAR_MAX_RANGE = 500
THERMAL_MAX_RANGE = 300
DRONE_MAX_RANGE = 2000

# Confidence requirements
SENSOR_CONFIDENCE_THRESHOLD = 0.7   # Must be >70% confident

# Grid for clustering
FUSION_GRID_SIZE = 10  # meters

# ============================================================================
# HAZARD PARAMETERS
# ============================================================================

# FIRE
FIRE_INITIAL_RADIUS = 30      # Starting size (meters)
FIRE_SPREAD_RATE = 0.5        # Expansion rate (m/s)
FIRE_MAX_RADIUS = 250         # Maximum size
FIRE_CRITICAL_RADIUS = 50     # Within this = immediate danger

# TOXIC GAS
GAS_INITIAL_RADIUS = 50
GAS_SPREAD_RATE = 0.2
GAS_MAX_RADIUS = 200
GAS_CRITICAL_RADIUS = 30

# ============================================================================
# BUILDING EXITS
# ============================================================================

EXIT_POSITIONS = [
    (0, 250),      # Left
    (500, 250),    # Right
    (250, 0),      # Top
    (250, 500),    # Bottom
]

EXIT_CAPACITY = 500  # People per minute per exit

# ============================================================================
# ALGORITHM-SPECIFIC PARAMETERS
# ============================================================================

# MANUAL DISPATCH (Baseline - how it's done today)
MANUAL_DISPATCH_UPDATE_INTERVAL = 60  # Check every 60 seconds (realistic delay)
MANUAL_DISPATCH_DETECTION_METHOD = "random"  # Detect victims randomly (911 calls)

# GREEDY ALGORITHM (Simple optimization - existing systems)
GREEDY_UPDATE_INTERVAL = 1.0  # Check every 1 second
GREEDY_NEAREST_RADIUS = 500   # Only consider nearby victims

# RS-SSTO (Our proposed algorithm)
RS_SSTO_PSO_UPDATE = 0.5   # Run PSO every 500ms
RS_SSTO_STO_UPDATE = 0.05  # Run STO every 50ms (10x faster!)
RS_SSTO_PANIC_UPDATE = 0.1 # Update panic every 100ms

# ============================================================================
# VISUALIZATION PARAMETERS
# ============================================================================

ANIMATION_FPS = 30                     # Frames per second
ANIMATION_SPEED_MULTIPLIER = 1.0       # 1.0=realtime, 2.0=2x faster

# Colors (RGB)
COLOR_VICTIM_CALM = (144, 238, 144)    # Green (panic < 0.3)
COLOR_VICTIM_STRESSED = (255, 255, 0)  # Yellow (panic 0.3-0.6)
COLOR_VICTIM_PANICKED = (255, 165, 0)  # Orange (panic 0.6-0.8)
COLOR_VICTIM_CRITICAL = (255, 0, 0)    # Red (panic > 0.8)
COLOR_TEAM = (0, 0, 255)               # Blue
COLOR_UNASSIGNED = (100, 100, 100)     # Gray
COLOR_HAZARD = (255, 69, 0)            # Orange-red
COLOR_EXIT = (0, 255, 0)               # Green

# ============================================================================
# LOGGING & OUTPUT
# ============================================================================

DEBUG_MODE = False                    # Verbose output?
PRINT_EVERY_N_SECONDS = 30            # Progress updates
SAVE_RESULTS_JSON = True              # Save results.json?
SAVE_PLOTS = True                     # Save PNG plots?
SAVE_VIDEO = False                    # Save MP4 video? (requires ffmpeg)

# ============================================================================
# SCENARIOS
# ============================================================================

SCENARIOS = {
    'building_fire': {
        'name': 'Large Office Building Fire',
        'victims': 4000,
        'trapped': 15,
        'teams': 15,
        'duration': 600,
    },
    'small_fire': {
        'name': 'Small Store Fire',
        'victims': 100,
        'trapped': 5,
        'teams': 5,
        'duration': 300,
    }
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    '''Check that all parameters make sense'''
    assert SIMULATION_DURATION > 0, "Duration must be positive"
    assert PSO_SWARM_SIZE >= 10, "PSO swarm too small (min 10)"
    assert NUM_RESCUE_TEAMS > 0, "Need at least 1 team"
    assert INITIAL_VICTIMS >= INITIAL_TRAPPED, "Trapped > total impossible"
    print("✓ Configuration validated")

validate_config()
```

This is your master configuration file. Every parameter is documented.
```

---

# STEP 3: CREATE data_structures.py

## Prompt 3: Data Structures - COMPLETE

```
Create file: simulation/data_structures.py

This defines the core classes: Victim, RescueTeam, Hazard, Exit, etc.

Copy this entire content:

"""
Core data structures for RS-SSTO Simulation

Classes defined:
- Victim: A person being evacuated or rescued
- RescueTeam: A team of rescuers
- Hazard: A danger zone (fire, gas, etc.)
- Exit: Building exit
- SimulationState: Snapshot of simulation at one moment
- AlgorithmResult: Final metrics from running one algorithm
"""

from dataclasses import dataclass, field
from enum import Enum
import uuid
from typing import Optional, List, Tuple
import math

# ============================================================================
# ENUMERATIONS
# ============================================================================

class VictimClassification(Enum):
    CONSCIOUS = "conscious"
    UNCONSCIOUS = "unconscious"
    TRAPPED_IN_RUBBLE = "trapped_rubble"
    DECEASED = "deceased"
    UNCERTAIN = "uncertain"

class HazardType(Enum):
    FIRE = "fire"
    TOXIC_GAS = "gas"
    STRUCTURAL_COLLAPSE = "collapse"

# ============================================================================
# VICTIM CLASS
# ============================================================================

@dataclass
class Victim:
    """
    Represents ONE person in the simulation.
    
    A victim is tracked from detection through evacuation/rescue.
    """
    
    # Identity
    id: str = field(default_factory=lambda: f"v_{str(uuid.uuid4())[:6]}")
    
    # Position & Movement
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    
    # Detection & Classification
    classification: VictimClassification = VictimClassification.CONSCIOUS
    fusion_confidence: float = 0.0
    vital_signs: float = 0.0
    detected_time: float = 0.0
    
    # Behavioral State
    panic_level: float = 0.5
    speed: float = 1.4
    is_moving: bool = True
    is_erratic: bool = False  # Jittery movement at high panic?
    
    # Assignments & Status
    assigned_team_id: Optional[str] = None
    group_id: Optional[str] = None
    
    evacuated: bool = False
    rescued: bool = False
    deceased: bool = False
    time_evacuated: Optional[float] = None
    
    # Tracking
    trajectory: List[Tuple[float, float]] = field(default_factory=list)
    
    def distance_to(self, ox: float, oy: float) -> float:
        return math.sqrt((self.x - ox)**2 + (self.y - oy)**2)
    
    def __repr__(self):
        status = "evacuated" if self.evacuated else "rescued" if self.rescued else "moving"
        return f"Victim({self.id}, pos=({self.x:.0f},{self.y:.0f}), panic={self.panic_level:.2f}, {status})"

# ============================================================================
# RESCUE TEAM CLASS
# ============================================================================

@dataclass
class RescueTeam:
    """
    Represents ONE rescue team in the simulation.
    
    Teams rescue victims, one at a time, in assigned order.
    """
    
    id: str = field(default_factory=lambda: f"t_{str(uuid.uuid4())[:6]}")
    
    # Position
    x: float = 250.0
    y: float = 250.0
    speed: float = 1.0
    
    # Assignments & Capacity
    assigned_victim_ids: List[str] = field(default_factory=list)
    current_victim_index: int = 0
    capacity: int = 3
    
    # Status
    busy: bool = False
    task_end_time: Optional[float] = None
    
    # Statistics
    victims_rescued: int = 0
    total_distance: float = 0.0
    total_time_working: float = 0.0
    
    trajectory: List[Tuple[float, float]] = field(default_factory=list)
    
    def distance_to(self, ox: float, oy: float) -> float:
        return math.sqrt((self.x - ox)**2 + (self.y - oy)**2)
    
    def __repr__(self):
        return f"Team({self.id}, pos=({self.x:.0f},{self.y:.0f}), assigned={len(self.assigned_victim_ids)}, rescued={self.victims_rescued})"

# ============================================================================
# HAZARD CLASS
# ============================================================================

@dataclass
class Hazard:
    """
    Represents a danger zone that expands over time.
    Examples: fire, toxic gas
    """
    
    id: str = field(default_factory=lambda: f"h_{str(uuid.uuid4())[:6]}")
    hazard_type: HazardType = HazardType.FIRE
    
    # Position & Size
    center_x: float = 0.0
    center_y: float = 0.0
    current_radius: float = 30.0
    
    # Spreading
    initial_radius: float = 30.0
    spread_rate: float = 0.5  # m/s
    max_radius: float = 250.0
    critical_radius: float = 50.0  # Immediately fatal
    
    # Status
    intensity: float = 1.0
    active: bool = True
    time_created: float = 0.0
    
    def distance_from_center(self, ox: float, oy: float) -> float:
        return math.sqrt((ox - self.center_x)**2 + (oy - self.center_y)**2)
    
    def is_immediately_dangerous(self, ox: float, oy: float) -> bool:
        return self.distance_from_center(ox, oy) < self.critical_radius
    
    def __repr__(self):
        return f"Hazard({self.hazard_type.value}, center=({self.center_x:.0f},{self.center_y:.0f}), radius={self.current_radius:.1f})"

# ============================================================================
# EXIT CLASS
# ============================================================================

@dataclass
class Exit:
    id: str = field(default_factory=lambda: f"exit_{str(uuid.uuid4())[:6]}")
    x: float = 0.0
    y: float = 0.0
    capacity: int = 500
    people_using: int = 0
    
    def distance_to(self, ox: float, oy: float) -> float:
        return math.sqrt((self.x - ox)**2 + (self.y - oy)**2)
    
    def __repr__(self):
        return f"Exit(pos=({self.x:.0f},{self.y:.0f}))"

# ============================================================================
# SIMULATION STATE CLASS
# ============================================================================

@dataclass
class SimulationState:
    """
    Complete snapshot of simulation at one moment.
    Contains all entities and metrics.
    """
    
    # Entities
    victims: List[Victim] = field(default_factory=list)
    teams: List[RescueTeam] = field(default_factory=list)
    hazards: List[Hazard] = field(default_factory=list)
    exits: List[Exit] = field(default_factory=list)
    
    current_time: float = 0.0
    
    # History for plotting
    time_history: List[float] = field(default_factory=list)
    detected_history: List[int] = field(default_factory=list)
    evacuated_history: List[int] = field(default_factory=list)
    rescued_history: List[int] = field(default_factory=list)
    casualties_history: List[int] = field(default_factory=list)
    avg_panic_history: List[float] = field(default_factory=list)
    
    def count_detected(self) -> int:
        return len([v for v in self.victims if v.detected_time > 0])
    
    def count_evacuated(self) -> int:
        return len([v for v in self.victims if v.evacuated])
    
    def count_rescued(self) -> int:
        return len([v for v in self.victims if v.rescued])
    
    def count_deceased(self) -> int:
        return len([v for v in self.victims if v.deceased])
    
    def get_avg_panic(self) -> float:
        if not self.victims:
            return 0.0
        return sum(v.panic_level for v in self.victims) / len(self.victims)
    
    def record_metrics(self):
        '''Save current state to history'''
        self.time_history.append(self.current_time)
        self.detected_history.append(self.count_detected())
        self.evacuated_history.append(self.count_evacuated())
        self.rescued_history.append(self.count_rescued())
        self.casualties_history.append(self.count_deceased())
        self.avg_panic_history.append(self.get_avg_panic())

# ============================================================================
# ALGORITHM RESULT CLASS
# ============================================================================

@dataclass
class AlgorithmResult:
    """Final results from running one algorithm"""
    
    algorithm_name: str
    total_evacuation_time: float
    total_rescue_time: float
    evacuated_count: int
    rescued_count: int
    casualties: int
    efficiency: float
    
    # History
    time_history: List[float] = field(default_factory=list)
    evacuated_history: List[int] = field(default_factory=list)
    rescued_history: List[int] = field(default_factory=list)
    casualties_history: List[int] = field(default_factory=list)
    avg_panic_history: List[float] = field(default_factory=list)
    
    def get_survival_rate(self, total: int) -> float:
        return (self.evacuated_count + self.rescued_count) / total if total > 0 else 0
    
    def get_casualty_rate(self, total: int) -> float:
        return self.casualties / total if total > 0 else 0
    
    def __repr__(self):
        return f"""
AlgorithmResult: {self.algorithm_name}
  Evacuation Time: {self.total_evacuation_time:.0f}s
  Evacuated: {self.evacuated_count}
  Rescued: {self.rescued_count}
  Casualties: {self.casualties}
  Efficiency: {self.efficiency:.2f}
"""
```

This creates all the basic classes used throughout simulation.
```

---

# STEP 4: CREATE algorithms/__init__.py

## Prompt 4: Algorithms Package Init

```
Create file: simulation/algorithms/__init__.py

Content (simple):

"""Algorithms package"""
from .base_algorithm import BaseAlgorithm
from .manual_dispatch import ManualDispatchAlgorithm
from .greedy_algorithm import GreedyAlgorithm
from .rs_ssto_algorithm import RSSTOAlgorithm

__all__ = ['BaseAlgorithm', 'ManualDispatchAlgorithm', 'GreedyAlgorithm', 'RSSTOAlgorithm']
```

This is just the package definition.
```

---

# STEP 5: CREATE algorithms/base_algorithm.py

## Prompt 5: Base Algorithm Class

```
Create file: simulation/algorithms/base_algorithm.py

This is the base class that all algorithms inherit from.
Copy this:

"""
Base class for all algorithms.

All algorithms (Manual, Greedy, RS-SSTO) inherit from this.
They all must implement the same interface: simulate()
"""

from abc import ABC, abstractmethod
from data_structures import SimulationState, AlgorithmResult
from config import *

class BaseAlgorithm(ABC):
    """
    Abstract base class for all algorithms.
    
    Each algorithm takes same input (victims, teams, hazards)
    and produces same output (AlgorithmResult with metrics).
    """
    
    def __init__(self):
        self.name = "BaseAlgorithm"
        self.description = "Abstract base"
        self.state = None
        self.metrics = {
            'time_history': [],
            'evacuated_history': [],
            'rescued_history': [],
            'casualties_history': [],
            'panic_history': []
        }
    
    @abstractmethod
    def simulate(self, state: SimulationState, duration: float) -> AlgorithmResult:
        """
        Run the algorithm on given state for given duration.
        
        Args:
            state: SimulationState with victims, teams, hazards, exits
            duration: How many seconds to simulate
            
        Returns:
            AlgorithmResult with final metrics
        """
        pass
    
    def _track_metrics(self, state: SimulationState):
        '''Record current statistics'''
        self.metrics['time_history'].append(state.current_time)
        self.metrics['evacuated_history'].append(state.count_evacuated())
        self.metrics['rescued_history'].append(state.count_rescued())
        self.metrics['casualties_history'].append(state.count_deceased())
        self.metrics['panic_history'].append(state.get_avg_panic())
    
    def _print_progress(self, current_time: float, total_time: float):
        '''Print progress to console'''
        if int(current_time) % 30 == 0:  # Every 30 seconds
            percent = (current_time / total_time) * 100
            print(f"[{self.name:20s}] {percent:3.0f}% | t={current_time:.0f}s", end='\r')
```

This is the base class all algorithms extend.
```

---

Due to character limits, I'll create a separate comprehensive file with all remaining prompts. Let me save what we have and continue.
