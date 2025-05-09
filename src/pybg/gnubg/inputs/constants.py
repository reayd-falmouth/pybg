# src/pybg/inputs/constants.py

# These constants map directly from eval.h and config.h
# Adjusted for Python naming conventions

NUM_POINTS = 25
NUM_SIDES = 2

# Constants for indexing input arrays
I_BEAROFF = 0
I_HOME_BOARD = 1
I_OPP_HOME_BOARD = 2
I_BLOCKING = 3
I_OPP_BLOCKING = 4
I_PRIME = 5
I_ANCHOR = 6
I_BACK_CHEQUER = 7
I_CONTAINMENT = 8
I_OPP_CONTAINMENT = 9
I_ADVANTAGE = 10
I_ADVANTAGE2 = 11
I_CONTACT = 12
I_OPP_CONTACT = 13
I_PIPCOUNT = 14
I_OPP_PIPCOUNT = 15
I_POSITION_CLASS = 16

# Constants for crash inputs (from inputs.c)
I_ACONTAIN2 = 17
MORE_INPUTS = 18

# For consistency with original C layout
INPUT_VECTOR_SIZE = 250

# Position classification enums (matching gnubg)
POS_CLASS_RACE = 0
POS_CLASS_CONTACT = 1
POS_CLASS_CRASHED = 2
POS_CLASS_BEAROFF = 3

# Misc values derived from gnubg source
MAX_CHECKERS = 15

# Debug labels for reverse indexing (optional, for debugging/logging)
INPUT_LABELS = [
    "BEAROFF", "HOME_BOARD", "OPP_HOME_BOARD", "BLOCKING", "OPP_BLOCKING",
    "PRIME", "ANCHOR", "BACK_CHEQUER", "CONTAINMENT", "OPP_CONTAINMENT",
    "ADVANTAGE", "ADVANTAGE2", "CONTACT", "OPP_CONTACT", "PIPCOUNT",
    "OPP_PIPCOUNT", "POSITION_CLASS", "ACONTAIN2"
]
