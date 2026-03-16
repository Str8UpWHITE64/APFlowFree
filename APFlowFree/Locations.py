from typing import Dict
from BaseClasses import Location


class APFlowFreeLocation(Location):
    game = "APFlowFree"


def build_main_locations(max_levels=20):
    """Mode 1: One location per level — 'Complete Level N' + 'Complete All Levels'"""
    locs = {}
    for lvl in range(1, max_levels + 1):
        locs[f"Complete Level {lvl}"] = 110000 + lvl
    locs["Complete All Levels"] = 119999
    return locs


def build_secondary_locations(max_levels=20):
    """Mode 2 extra checks: 'Complete Level N Check 2'"""
    return {
        f"Complete Level {lvl} Check 2": 111000 + lvl
        for lvl in range(1, max_levels + 1)
    }


def build_individual_locations(max_levels=20, max_stages=20):
    """Mode 3: One location per stage — 'Level N Stage S Complete' + 'Complete All Levels'"""
    locs = {}
    for lvl in range(1, max_levels + 1):
        for stg in range(1, max_stages + 1):
            loc_id = 100000 + (lvl - 1) * max_stages + (stg - 1)
            locs[f"Level {lvl} Stage {stg} Complete"] = loc_id
    locs["Complete All Levels"] = 109999
    return locs


# Pre-build the dicts so they can be imported as module-level constants
MAIN_LEVEL_COMPLETION_DICT: Dict[str, int] = build_main_locations()
SECONDARY_LEVEL_COMPLETION_DICT: Dict[str, int] = build_secondary_locations()
INDIVIDUAL_STAGE_COMPLETION_DICT: Dict[str, int] = build_individual_locations()
