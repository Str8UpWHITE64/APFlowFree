from BaseClasses import Item, ItemClassification


class APFlowFreeItem(Item):
    game = "APFlowFree"


def build_level_items(max_levels=20):
    """Mode 1: One item per level — 'Level N Stages'"""
    return {
        f"Level {lvl} Stages": (11000 + lvl, ItemClassification.progression)
        for lvl in range(1, max_levels + 1)
    }


def build_half_items(max_levels=20):
    """Mode 2: Two items per level — 'Level N Stages First Half / Second Half'"""
    items = {}
    for lvl in range(1, max_levels + 1):
        base = 12000 + (lvl - 1) * 2
        items[f"Level {lvl} Stages First Half"] = (base, ItemClassification.progression)
        items[f"Level {lvl} Stages Second Half"] = (base + 1, ItemClassification.progression)
    return items


def build_stage_items(max_levels=20, max_stages=20):
    """Mode 3: One item per stage — 'Level 1 Stages' + 'Level N Stage S' for levels 2+"""
    items = {
        "Level 1 Stages": (10000, ItemClassification.progression)
    }
    for lvl in range(2, max_levels + 1):
        for stg in range(1, max_stages + 1):
            item_id = 10000 + (lvl - 1) * max_stages + stg
            items[f"Level {lvl} Stage {stg}"] = (item_id, ItemClassification.progression)
    return items


def build_filler_items():
    return {
        "Flow Bonus": (13000, ItemClassification.filler)
    }


def build_trap_items():
    """Traps (id band 14000+). All client-side visual/UX effects; never touch saved progress or logic."""
    return {
        "Board Clear Trap": (14001, ItemClassification.trap),    # clears the in-progress board
        "Fog Trap": (14002, ItemClassification.trap),            # fades the grid + endpoints briefly
        "Color Shuffle Trap": (14003, ItemClassification.trap),  # scrambles the pipe colors briefly
        "Grayscale Trap": (14004, ItemClassification.trap),      # drains all color for ~15s
    }


def build_useful_items():
    """Consumable helpers (id band 15000+). The player banks these and spends them via a button."""
    return {
        "Solve Random Pipe": (15001, ItemClassification.useful),  # solves one random unsolved pipe
        "Skip Puzzle": (15002, ItemClassification.useful),        # instantly completes the current stage
    }


# Pre-build the dicts so they can be imported as module-level constants
ITEMS = build_level_items()
ITEMS_B = build_half_items()
ITEMS_C = build_stage_items()
ITEMS_FILLER = build_filler_items()
ITEMS_TRAPS = build_trap_items()
ITEMS_USEFUL = build_useful_items()
