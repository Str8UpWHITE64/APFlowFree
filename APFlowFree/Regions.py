from BaseClasses import Region, Location
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

    if menu_region not in multiworld.regions:
        multiworld.regions.append(menu_region)
    if levels_region not in multiworld.regions:
        multiworld.regions.append(levels_region)

    # Connect the regions so that the player goes from Menu to Levels.
    menu_region.connect(levels_region)

    # Build a list of progression location names that should receive items.
    progression_loc_names = []

    if stage_sanity == 1:
        # For each level selected by the player, add the corresponding main check.
        for level in range(1, num_levels + 1):
            main_key = f"Complete Level {level}"
            if main_key in MAIN_LEVEL_COMPLETION_DICT:
                loc_id = MAIN_LEVEL_COMPLETION_DICT[main_key]
                location_obj = APFlowFreeLocation(player, main_key, loc_id, parent=levels_region)
                levels_region.locations.append(location_obj)
                progression_loc_names.append(main_key)
            else:
                print(f"[Warning] {main_key} not found in MAIN_LEVEL_COMPLETION_DICT.")

        # Always add the final overall check for completing all levels.
        all_levels_key = "Complete All Levels"
        if all_levels_key in MAIN_LEVEL_COMPLETION_DICT:
            location_obj = APFlowFreeLocation(player, all_levels_key, None, parent=levels_region)
            location_obj.event = True  # <--- this is the important part!
            levels_region.locations.append(location_obj)
            progression_loc_names.append(all_levels_key)

    elif stage_sanity == 2:
        # For each level selected by the player, add the corresponding main check.
        for level in range(1, num_levels + 1):
            main_key = f"Complete Level {level}"
            if main_key in MAIN_LEVEL_COMPLETION_DICT:
                loc_id = MAIN_LEVEL_COMPLETION_DICT[main_key]
                location_obj = APFlowFreeLocation(player, main_key, loc_id, parent=levels_region)
                levels_region.locations.append(location_obj)
                progression_loc_names.append(main_key)
            else:
                print(f"[Warning] {main_key} not found in MAIN_LEVEL_COMPLETION_DICT.")

            secondary_key = f"Complete Level {level} Check 2"
            if secondary_key in SECONDARY_LEVEL_COMPLETION_DICT:
                loc_id = SECONDARY_LEVEL_COMPLETION_DICT[secondary_key]
                location_obj = APFlowFreeLocation(player, secondary_key, loc_id, parent=levels_region)
                levels_region.locations.append(location_obj)
                progression_loc_names.append(secondary_key)
            else:
                print(f"[Warning] {secondary_key} not found in SECONDARY_LEVEL_COMPLETION_DICT.")

        # Always add the final overall check for completing all levels.
        all_levels_key = "Complete All Levels"
        if all_levels_key in MAIN_LEVEL_COMPLETION_DICT:
            location_obj = APFlowFreeLocation(player, all_levels_key, None, parent=levels_region)
            location_obj.event = True  # <--- this is the important part!
            levels_region.locations.append(location_obj)
            progression_loc_names.append(all_levels_key)

    elif stage_sanity == 3:
        for i in range(1, num_levels + 1):
            for j in range(1, num_stages + 1):
                if f"Level {i} Stage {j} Complete" in INDIVIDUAL_STAGE_COMPLETION_DICT:
                    loc_id = INDIVIDUAL_STAGE_COMPLETION_DICT[f"Level {i} Stage {j} Complete"]
                    location_obj = APFlowFreeLocation(player, f"Level {i} Stage {j} Complete", loc_id, parent=levels_region)
                    levels_region.locations.append(location_obj)
                    progression_loc_names.append(f"Level {i} Stage {j} Complete")

        # Always add the final overall check for completing all levels.
        all_levels_key = "Complete All Levels"
        if all_levels_key in INDIVIDUAL_STAGE_COMPLETION_DICT:
            location_obj = APFlowFreeLocation(player, all_levels_key, None, parent=levels_region)
            location_obj.event = True  # <--- this is the important part!
            levels_region.locations.append(location_obj)
            progression_loc_names.append(all_levels_key)

    # Store only these progression locations so that the dummy Menu location does not count.
    multiworld.worlds[player].progression_locations = progression_loc_names

    print(f"[Player {player}] Final progression locations: {progression_loc_names}")