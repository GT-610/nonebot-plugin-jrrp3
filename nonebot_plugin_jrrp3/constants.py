from enum import IntEnum

class LuckValueBounds(IntEnum):
    MIN_SAFE = -1_000_000
    MAX_SAFE = 1_000_000
    RANDINT_FALLBACK_MIN = 1
    RANDINT_FALLBACK_MAX = 100

class WeekDay(IntEnum):
    MONDAY = 0
    SUNDAY = 6
