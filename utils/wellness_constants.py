"""
utils/wellness_constants.py
============================
Domain constants and preset configurations for Milestone 8 (Wellness Hub).
"""

BREATHING_PATTERNS = {
    "box": {
        "title": "Box Breathing",
        "description": "Equal parts inhale, hold, exhale, hold for focus and acute stress reduction.",
        "config": {"inhale_sec": 4, "hold_in_sec": 4, "exhale_sec": 4, "hold_out_sec": 4},
        "default_cycles": 10
    },
    "4-7-8": {
        "title": "4-7-8 Relaxing Breath",
        "description": "Natural tranquilizer for the nervous system, ideal for anxiety and sleep preparation.",
        "config": {"inhale_sec": 4, "hold_in_sec": 7, "exhale_sec": 8, "hold_out_sec": 0},
        "default_cycles": 8
    },
    "calm": {
        "title": "Calm Breathing",
        "description": "Smooth, rhythmic breathing to lower heart rate and soothe stress.",
        "config": {"inhale_sec": 4, "hold_in_sec": 2, "exhale_sec": 4, "hold_out_sec": 0},
        "default_cycles": 12
    },
    "deep_relaxation": {
        "title": "Deep Relaxation",
        "description": "Extended exhale pattern designed for deep parasympathetic activation.",
        "config": {"inhale_sec": 4, "hold_in_sec": 0, "exhale_sec": 8, "hold_out_sec": 0},
        "default_cycles": 10
    }
}

FOCUS_PRESETS = {
    "pomodoro": {
        "title": "Classic Pomodoro",
        "work_duration_minutes": 25,
        "break_duration_minutes": 5,
        "description": "25 minutes of deep focus followed by a 5 minute break."
    },
    "deep_work": {
        "title": "Deep Work Block",
        "work_duration_minutes": 50,
        "break_duration_minutes": 10,
        "description": "50 minutes of uninterrupted work with a 10 minute rest."
    }
}

MUSIC_CATEGORIES = [
    "stress_relief",
    "calm",
    "focus",
    "nature",
    "morning_energy"
]

WELLNESS_ACTIVITIES = [
    "hydrate",
    "stretch",
    "journal",
    "breathing",
    "meditation",
    "focus",
    "music"
]

# Weights used for Wellness Score Engine (Total = 1.0)
WELLNESS_SCORE_WEIGHTS = {
    "sleep": 0.30,
    "mood": 0.25,
    "mindfulness": 0.20,
    "activity": 0.15,
    "focus": 0.10
}
