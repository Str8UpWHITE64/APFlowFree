from BaseClasses import Region
from .Locations import (
    MAIN_LEVEL_COMPLETION_DICT,
    SECONDARY_LEVEL_COMPLETION_DICT,
    APFlowFreeLocation, INDIVIDUAL_STAGE_COMPLETION_DICT
)


def create_apflowfree_regions(multiworld, player):

    # Retrieve player options.
    options = multiworld.worlds[player].options
    num_levels = options.levels.value
    num_stages = options.stages_per_level.value
    stage_sanity = options.stage_sanity.value

    # Create the Menu region and Levels region.
    menu_region = Region("Menu", player, multiworld)
    levels_region = Region("Levels", player, multiworld)
    multiworld.regions += [menu_region, levels_region]

    # Connect the regions so that the player goes from Menu to Levels.
    menu_region.connect(levels_region)

    # Build the list of location names (and their ids) for the chosen stage_sanity.
    loc_ids = {}
    if stage_sanity in (1, 2):
        for level in range(1, num_levels + 1):
            name = f"Complete Level {level}"
            loc_ids[name] = MAIN_LEVEL_COMPLETION_DICT[name]
            if stage_sanity == 2:
                name = f"Complete Level {level} Check 2"
                loc_ids[name] = SECONDARY_LEVEL_COMPLETION_DICT[name]
    elif stage_sanity == 3:
        for i in range(1, num_levels + 1):
            for j in range(1, num_stages + 1):
                name = f"Level {i} Stage {j} Complete"
                loc_ids[name] = INDIVIDUAL_STAGE_COMPLETION_DICT[name]

    for name, loc_id in loc_ids.items():
        levels_region.locations.append(APFlowFreeLocation(player, name, loc_id, parent=levels_region))

    # The victory event (no address): its access rule and locked "Victory" item are set in Rules.py.
    levels_region.locations.append(APFlowFreeLocation(player, "Complete All Levels", None, parent=levels_region))

    # Store the progression location names (plus the victory event, which Rules.py filters out).
    multiworld.worlds[player].progression_locations = list(loc_ids) + ["Complete All Levels"]
