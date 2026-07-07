from dataclasses import dataclass
from Options import Choice, Range, Toggle, DeathLink, PerGameCommonOptions


class Levels(Range):
    """Customize the number of levels (1-20)."""
    display_name = "Levels"
    range_start = 1
    range_end = 20
    default = 10

class StagesPerLevel(Range):
    """Customize the number of stages per level (1-20)."""
    display_name = "Stages Per Level"
    range_start = 1
    range_end = 20
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
    2. Complete a percentage of Stages Per Level (see Goal Percentage)
    3. Complete a percentage of Levels (see Goal Percentage)"""
    display_name = "Goal"
    option_1 = 1
    option_2 = 2
    option_3 = 3
    default = 1

class GoalPercentage(Range):
    """For Goal options 2 and 3, the percentage of stages-per-level / levels required to win.
    Ignored for Goal 1, which always requires 100%."""
    display_name = "Goal Percentage"
    range_start = 50
    range_end = 100
    default = 80

class MinPairs(Range):
    """Number of color pairs on the first level's boards. The board grid is (pairs + 2) cells per side,
    so larger values mean bigger, harder, slower-to-generate puzzles."""
    display_name = "Minimum Color Pairs"
    range_start = 2
    range_end = 20
    default = 3

class MaxPairs(Range):
    """Number of color pairs on the last level's boards. The board grid is (pairs + 2) cells per side.\n
    DISCLAIMER: large boards are slow to build. Values around 16+ can freeze the page for several
    seconds while each stage generates (a loading spinner is shown), and the cells get small on
    screen. 12 is a comfortable default; raise this only if you want big, tougher puzzles."""
    display_name = "Maximum Color Pairs"
    range_start = 2
    range_end = 20
    default = 12

class DifficultyCurve(Choice):
    """How board size ramps from Minimum Color Pairs (level 1) up to Maximum Color Pairs (last level).\n
    linear: even steps.
    gentle: stays small longer, then grows quickly near the end.
    steep: grows quickly early, then eases off."""
    display_name = "Difficulty Curve"
    option_linear = 0
    option_gentle = 1
    option_steep = 2
    default = 0

class TrapPercentage(Range):
    """Percentage of the filler items REMAINING after helper items that become traps. 0 disables traps.
    Traps are harmless, time-limited visual effects (Board Clear, Fog, Color Shuffle, Grayscale) that
    never affect your saved progress or the multiworld logic."""
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0

class SolveRandomPipeCount(Range):
    """How many 'Solve Random Pipe' helper items to add to the pool. Each one, when spent, instantly
    solves one random unsolved pipe on the board you're currently playing. 0 = none.
    If this plus Skip Puzzle Charges exceeds the available filler, both are scaled down to fit while
    keeping their ratio."""
    display_name = "Solve Random Pipe Charges"
    range_start = 0
    range_end = 50
    default = 0

class SkipPuzzleCount(Range):
    """How many 'Skip Puzzle' helper items to add to the pool. Each one, when spent, instantly
    completes the stage you're currently on (and sends its check). 0 = none.
    If this plus Solve Random Pipe Charges exceeds the available filler, both are scaled down to fit
    while keeping their ratio."""
    display_name = "Skip Puzzle Charges"
    range_start = 0
    range_end = 20
    default = 0

class StartingLevels(Range):
    """How many levels are unlocked from the very start, with no unlock item required. Default 1 (only Level 1).
    Clamped to the number of levels."""
    display_name = "Starting Levels"
    range_start = 1
    range_end = 20
    default = 1


@dataclass
class APFlowFreeOptions(PerGameCommonOptions):
    levels: Levels
    stages_per_level: StagesPerLevel
    stage_sanity: StageSanity
    strict_mode: StrictMode
    goal: Goal
    goal_percentage: GoalPercentage
    min_pairs: MinPairs
    max_pairs: MaxPairs
    difficulty_curve: DifficultyCurve
    starting_levels: StartingLevels
    trap_percentage: TrapPercentage
    solve_random_pipe_count: SolveRandomPipeCount
    skip_puzzle_count: SkipPuzzleCount
    death_link: DeathLink
