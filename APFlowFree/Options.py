from dataclasses import dataclass
from Options import Choice, PerGameCommonOptions


class Levels(Choice):
    """Customize the number of levels."""
    display_name = "Levels"
    option_5 = 5
    option_6 = 6
    option_7 = 7
    option_8 = 8
    option_9 = 9
    option_10 = 10
    option_20 = 20
    default = 10

class StagesPerLevel(Choice):
    """Customize the number of stages per level."""
    display_name = "Stages Per Level"
    option_5 = 5
    option_6 = 6
    option_7 = 7
    option_8 = 8
    option_9 = 9
    option_10 = 10
    option_20 = 20
    default = 10

class StageSanity(Choice):
    """Customize the number of items your stages and levels are locked behind.\n
    1. All stages are in the single level item.
    2. Stages are broken in half per level. ie: Level 1 Stages 1 will have stages 1-5, Level 1 Stages 2 will have stages 6-10, etc.
    3. Stages are broken into individual items.  Warning, this can be a lot of items. If you have 20 Levels and 20 Stages, that's 400 items added to the pool."""
    option_1 = 1
    option_2 = 2
    option_3 = 3
    default = 1

class StrictMode(Choice):
    """Customize whether strict mode is enabled.\n
    Strict mode prevents a puzzle from being marked as complete if any of the lines run parallel to themselves. This should force the player to solve the puzzle closer to how the puzzle was generated.\n
    1. Disabled
    2. Enabled"""
    display_name = "Strict Mode"
    option_1 = 1
    option_2 = 2
    default = 1

class Goal(Choice):
    """Customize the goal for the game.\n
    1. Complete All Levels and Stages
    2. Complete 80% of Stages Per Level
    3. Complete 80% of Levels"""
    display_name = "Goal"
    option_1 = 1
    option_2 = 2
    option_3 = 3
    default = 1


@dataclass
class APFlowFreeOptions(PerGameCommonOptions):
    levels: Levels
    stages_per_level: StagesPerLevel
    stage_sanity: StageSanity
    strict_mode: StrictMode
    goal: Goal