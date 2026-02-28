"""
RS-SSTO Simulation — Global Configuration
==========================================
All tuneable parameters for the evacuation simulation.
"""

# ─── Window / Map ────────────────────────────────────────────────────────────
MAP_WIDTH  = 800          # pixels
MAP_HEIGHT = 600          # pixels
FPS        = 60           # pygame frame-rate

# ─── Agents ──────────────────────────────────────────────────────────────────
NUM_AGENTS       = 50
AGENT_RADIUS     = 4      # draw radius (px)
AGENT_MAX_SPEED  = 3.0    # px / frame
AGENT_MASS       = 1.0

# ─── Exit ────────────────────────────────────────────────────────────────────
EXIT_POS    = (780, 300)  # right-centre
EXIT_RADIUS = 30          # capture radius

# ─── Hazard ──────────────────────────────────────────────────────────────────
HAZARD_POS    = (400, 300)
HAZARD_RADIUS = 60

# ─── Obstacles (random rectangles will be generated) ─────────────────────────
NUM_OBSTACLES   = 5
OBS_MIN_SIZE    = 30
OBS_MAX_SIZE    = 80

# ─── Social Force Model ─────────────────────────────────────────────────────
SFM_DESIRED_SPEED  = 2.5
SFM_RELAX_TIME     = 0.5
SFM_REPULSION_A    = 2000.0
SFM_REPULSION_B    = 0.08

# ─── PSO ─────────────────────────────────────────────────────────────────────
PSO_W   = 0.5        # inertia
PSO_C1  = 1.5        # cognitive
PSO_C2  = 2.0        # social

# ─── ACO ─────────────────────────────────────────────────────────────────────
ACO_EVAPORATION  = 0.05
ACO_DEPOSIT      = 10.0
ACO_GRID         = 20      # pheromone grid cell size (px)
ACO_ALPHA        = 1.0     # pheromone influence
ACO_BETA         = 2.0     # heuristic influence

# ─── APF ─────────────────────────────────────────────────────────────────────
APF_ATTRACT_GAIN  = 0.9
APF_REPULSE_GAIN  = 5000.0
APF_REPULSE_RANGE = 60.0

# ─── RS-SSTO (proposed) ─────────────────────────────────────────────────────
RSSTO_SWARM_W      = 0.4
RSSTO_SWARM_C1     = 0.8
RSSTO_SWARM_C2     = 1.5
RSSTO_TENSION_K    = 1.8     # surface-tension repulsion coefficient
RSSTO_SAFE_DIST    = 18.0    # safe inter-agent spacing (px)
RSSTO_PANIC_ALPHA  = 0.5     # density weight in panic
RSSTO_PANIC_BETA   = 0.5     # hazard weight in panic

# ─── Simulation ─────────────────────────────────────────────────────────────
MAX_FRAMES = 3000        # safety cut-off per algorithm run

# ─── Colours (R, G, B) ──────────────────────────────────────────────────────
COL_BG      = (30, 30, 30)
COL_AGENT   = (0, 200, 255)
COL_EXIT    = (0, 255, 80)
COL_HAZARD  = (255, 60, 30)
COL_OBS     = (120, 120, 120)
COL_TEXT    = (240, 240, 240)
