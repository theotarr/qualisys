"""This file contains the labels for the 18 body markers used in the motion capture system in the correct index."""

LABELS = [
    "RAC",
    "LAC",
    "RAS",
    "RPS",
    "LAS",
    "LPS",
    # "RME",
    # "RLE",
    # "LME",
    # "LLE",
    "RLW",
    "RMW",
    "LLW",
    "LMW",
    "RAE",
    "RPE",
    "LAE",
    "LPE",
]

RIGHT_SHOULDER_LABELS = [LABELS.index("RAS"), LABELS.index("RPS")]
LEFT_SHOULDER_LABELS = [LABELS.index("LAS"), LABELS.index("LPS")]
RIGHT_COM_LABELS = [LABELS.index("RAE"), LABELS.index("RPE")]
LEFT_COM_LABELS = [LABELS.index("LAE"), LABELS.index("LPE")]
