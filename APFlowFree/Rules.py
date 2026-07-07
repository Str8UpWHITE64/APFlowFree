from BaseClasses import MultiWorld, Item, ItemClassification
from worlds.generic.Rules import add_item_rule
import math
import re


def apply_rules(multiworld: MultiWorld, player: int):
    world = multiworld.worlds[player]
    num_levels = world.options.levels.value
    num_stages = world.options.stages_per_level.value
    stage_sanity = world.options.stage_sanity.value
    # Levels 1..starting_levels are free (no unlock item gates them); gating begins at the next level.
    starting_levels = min(world.options.starting_levels.value, num_levels)

    # ---------------------------------------------------------------
    # 1) Access rules — require the matching item before a location
    #    can be checked.  Level 1 is always open (no item gates it).
    # ---------------------------------------------------------------

    if stage_sanity == 1:
        # Items: "Level N Stages" (N = 2..num_levels)
        # Locations: "Complete Level N" (N = 1..num_levels)
        for L in range(starting_levels + 1, num_levels + 1):
            item_name = f"Level {L} Stages"
            loc = multiworld.get_location(f"Complete Level {L}", player)
            loc.access_rule = lambda state, iname=item_name: state.has(iname, player)

    elif stage_sanity == 2:
        # Items: "Level N Stages First Half" / "Level N Stages Second Half" (N = 2..num_levels)
        # Locations: "Complete Level N" + "Complete Level N Check 2" (N = 1..num_levels)
        for L in range(starting_levels + 1, num_levels + 1):
            item_first = f"Level {L} Stages First Half"
            item_second = f"Level {L} Stages Second Half"

            loc_main = multiworld.get_location(f"Complete Level {L}", player)
            loc_main.access_rule = lambda state, iname=item_first: state.has(iname, player)

            loc_check2 = multiworld.get_location(f"Complete Level {L} Check 2", player)
            loc_check2.access_rule = lambda state, iname=item_second: state.has(iname, player)

    elif stage_sanity == 3:
        # Items: "Level N Stage S" (N = 2..num_levels, S = 1..num_stages)
        # Locations: "Level N Stage S Complete" (N = 1..num_levels, S = 1..num_stages)
        for L in range(starting_levels + 1, num_levels + 1):
            for S in range(1, num_stages + 1):
                item_name = f"Level {L} Stage {S}"
                loc = multiworld.get_location(f"Level {L} Stage {S} Complete", player)
                loc.access_rule = lambda state, iname=item_name: state.has(iname, player)

    # ---------------------------------------------------------------
    # 2) Victory condition — "Complete All Levels" event location
    # ---------------------------------------------------------------
    try:
        complete_all_loc = multiworld.get_location("Complete All Levels", player)
    except KeyError:
        return

    # Build the set of locations that must be reachable to win, based on the goal:
    #   goal 1 = complete everything (all stages/levels)
    #   goal 2 = complete 80% of the stages in every level. This is only representable as
    #            location checks under stage_sanity 3 (one location per stage); for
    #            stage_sanity 1/2 it collapses to full completion so that the apworld's
    #            completion_condition and the client's StatusUpdate(CLIENT_GOAL) agree.
    #   goal 3 = fully complete 80% of the levels.
    # A FIXED canonical subset is chosen (first N stages / first N levels) so the access
    # rule stays monotonic, which AP's fill requires. Thresholds mirror the client's
    # Math.floor(x*0.8 + 0.5) in maybeSendGoalIfMet so the two never disagree.
    goal = world.options.goal.value
    goal_percentage = world.options.goal_percentage.value
    all_locs = [loc for loc in world.progression_locations if loc != "Complete All Levels"]

    def _num_after(label, loc_name):
        m = re.search(label + r" (\d+)", loc_name)
        return int(m.group(1)) if m else None

    if goal == 3:
        lvl_thr = max(1, min(num_levels, int(num_levels * goal_percentage / 100 + 0.5)))
        required = [loc for loc in all_locs if (_num_after("Level", loc) or 0) <= lvl_thr]
    elif goal == 2 and stage_sanity == 3:
        stage_thr = max(1, min(num_stages, int(num_stages * goal_percentage / 100 + 0.5)))
        required = [loc for loc in all_locs if (_num_after("Stage", loc) or 0) <= stage_thr]
    else:
        required = list(all_locs)

    complete_all_loc.access_rule = lambda state: all(
        state.can_reach(loc, "Location", player) for loc in required
    )

    complete_all_loc.place_locked_item(
        Item("Victory", ItemClassification.progression, None, player)
    )
    multiworld.completion_condition[player] = lambda state: state.has("Victory", player)

    # ---------------------------------------------------------------
    # 3) Self-lock prevention — forbid placing a level's unlock item
    #    at its own completion location (extra safety net).
    # ---------------------------------------------------------------

    def _forbid_item_at_location(item_name: str, location_name: str):
        try:
            loc = multiworld.get_location(location_name, player)
        except KeyError:
            return
        add_item_rule(
            loc,
            lambda it, iname=item_name: not (it.player == player and it.name == iname)
        )

    if stage_sanity == 1:
        for L in range(starting_levels + 1, num_levels + 1):
            _forbid_item_at_location(f"Level {L} Stages", f"Complete Level {L}")

    elif stage_sanity == 2:
        for L in range(starting_levels + 1, num_levels + 1):
            _forbid_item_at_location(f"Level {L} Stages First Half", f"Complete Level {L}")
            _forbid_item_at_location(f"Level {L} Stages Second Half", f"Complete Level {L} Check 2")

    elif stage_sanity == 3:
        for L in range(starting_levels + 1, num_levels + 1):
            for S in range(1, num_stages + 1):
                _forbid_item_at_location(f"Level {L} Stage {S}", f"Level {L} Stage {S} Complete")
