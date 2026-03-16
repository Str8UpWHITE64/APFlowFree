from BaseClasses import MultiWorld, Item, ItemClassification
from worlds.generic.Rules import add_item_rule
import math

def apply_rules(multiworld: MultiWorld, player: int):
    # --- Victory condition as you had it ---
    try:
        complete_all_loc = multiworld.get_location("Complete All Levels", player)
    except KeyError:
        return

    required = [
        loc for loc in multiworld.worlds[player].progression_locations
        if loc != "Complete All Levels"
    ]
    complete_all_loc.access_rule = lambda state: all(
        state.can_reach(loc, "Location", player) for loc in required
    )

    complete_all_loc.address = None
    complete_all_loc.place_locked_item(
        Item("Victory", ItemClassification.progression, None, player)
    )
    multiworld.completion_condition[player] = lambda state: state.has("Victory", player)

    # --- NEW: forbid self-lock placements ---
    world = multiworld.worlds[player]
    num_levels = world.options.levels.value
    num_stages = world.options.stages_per_level.value
    stage_sanity = world.options.stage_sanity.value  # 1, 2, or 3

    # Helper to forbid a single item name at a single location name (for this player only)
    def _forbid_item_at_location(item_name: str, location_name: str):
        # Location might not exist if not generated for this mode; guard safely.
        try:
            loc = multiworld.get_location(location_name, player)
        except KeyError:
            return
        add_item_rule(
            loc,
            # allow item if it's not the forbidden one for this player
            lambda it: not (it.player == player and it.name == item_name)
        )

    if stage_sanity == 1:
        # Items (for levels 2..N): "Level L Stages"
        # Locations (for levels 1..N): "Complete Level L"
        for L in range(2, num_levels + 1):
            item_name = f"Level {L} Stages"
            location_name = f"Complete Level {L}"
            # Forbid placing the item that unlocks Level L behind completing Level L
            _forbid_item_at_location(item_name, location_name)

    elif stage_sanity == 2:
        # Split stages into two halves
        first_end = math.ceil(num_stages / 2)

        for L in range(1, num_levels + 1):
            # Locations you currently generate:
            loc_main = f"Complete Level {L}"
            loc_second = f"Complete Level {L} Check 2"

            # Items exist only for levels 2..N
            if L >= 2:
                # First-half item -> forbid at first (main) location
                item_first = f"Level {L} Stages 1-{first_end}"
                _forbid_item_at_location(item_first, loc_main)

                # Second-half item (only if there actually is a second half)
                if first_end < num_stages:
                    item_second = f"Level {L} Stages {first_end + 1}-{num_stages}"
                    _forbid_item_at_location(item_second, loc_second)

    elif stage_sanity == 3:
        # One item per stage for levels 2..N
        # Locations you generate: "Level L Stage S Complete" for levels 1..N
        for L in range(1, num_levels + 1):
            for S in range(1, num_stages + 1):
                loc_name = f"Level {L} Stage {S} Complete"
                if L >= 2:
                    item_name = f"Level {L} Stage {S}"
                    _forbid_item_at_location(item_name, loc_name)