from worlds.AutoWorld import World
from BaseClasses import Item, ItemClassification, MultiWorld
from .Items import ITEMS, ITEMS_B, ITEMS_C, ITEMS_FILLER, ITEMS_TRAPS, ITEMS_USEFUL, APFlowFreeItem
from .Locations import MAIN_LEVEL_COMPLETION_DICT, SECONDARY_LEVEL_COMPLETION_DICT, INDIVIDUAL_STAGE_COMPLETION_DICT
from .Options import APFlowFreeOptions
from .Rules import apply_rules


class APFlowFreeWorld(World):
    game = "APFlowFree"
    options_dataclass = APFlowFreeOptions
    options = APFlowFreeOptions

    # Create a mapping from item names to their unique IDs
    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    item_name_to_id.update({name: data[0] for name, data in ITEMS_B.items()})
    item_name_to_id.update({name: data[0] for name, data in ITEMS_C.items()})
    item_name_to_id.update({name: data[0] for name, data in ITEMS_FILLER.items()})
    item_name_to_id.update({name: data[0] for name, data in ITEMS_TRAPS.items()})
    item_name_to_id.update({name: data[0] for name, data in ITEMS_USEFUL.items()})

    # Use both MAIN_LEVEL_COMPLETION_DICT and SECONDARY_LEVEL_COMPLETION_DICT to create a mapping for locations
    location_name_to_id = {name: data for name, data in MAIN_LEVEL_COMPLETION_DICT.items()}
    location_name_to_id.update({name: data for name, data in SECONDARY_LEVEL_COMPLETION_DICT.items()})
    location_name_to_id.update({name: data for name, data in INDIVIDUAL_STAGE_COMPLETION_DICT.items()})

    def create_item(self, name: str, classification: ItemClassification = ItemClassification.filler) -> APFlowFreeItem:
        """
        Create an instance of an APFlowFreeItem.
        """
        if name in self.item_name_to_id:
            item_id = self.item_name_to_id[name]
        else:
            raise ValueError(f"Item '{name}' not found in ITEMS!")
        return APFlowFreeItem(name, classification, item_id, self.player)

    def create_items(self):
        selected_names = []

        # Build the item pool for the multiworld based on the player's selected number of levels.
        multiworld = self.multiworld
        player = self.player

        # Retrieve the number of levels, stages, and stage sanity setting from the player's options.
        num_levels = self.options.levels.value
        num_stages = self.options.stages_per_level.value
        stage_sanity = self.options.stage_sanity.value
        # Levels 1..start are free (no unlock item); unlock items begin at start+1.
        start = min(self.options.starting_levels.value, num_levels)

        if stage_sanity == 1:
            # Build a list of stage item names for the selected levels.
            selected_names = [f"Level {i} Stages" for i in range(start + 1, num_levels + 1)]

        elif stage_sanity == 2:
            for i in range(start + 1, num_levels + 1):
                selected_names.append(f"Level {i} Stages First Half")
                selected_names.append(f"Level {i} Stages Second Half")

        elif stage_sanity == 3:
            for i in range(start + 1, num_levels + 1):
                for j in range(1, num_stages + 1):
                    selected_names.append(f"Level {i} Stage {j}")

        # Create the base item pool using the defined stage items.
        itempool = []
        for name in selected_names:
            try:
                item = self.create_item(name, ItemClassification.progression)
            except ValueError:
                # If an expected key is not found in the ITEMS dict, use a filler as a fallback.
                # You might choose a more robust fallback strategy here.
                item = APFlowFreeItem("Flow Bonus", ItemClassification.filler, 13000, player)
            itempool.append(item)

        # Determine how many progression locations were generated in Regions.py.
        progression_count = len(multiworld.worlds[player].progression_locations) - 1

        # Fill the remaining (non-progression) slots. Everything replaces filler 1:1, so the total
        # item count always equals the fillable-location count (no FillError).
        #   1. Useful helper items take their requested counts. If the combined request overflows the
        #      available pool, scale both down proportionally so their RATIO is preserved (e.g. asking
        #      for 10 solve + 15 skip in a 20-slot pool -> 40%/60% -> 8 solve + 12 skip).
        #   2. Traps take a percentage of the filler that REMAINS after useful items.
        #   3. "Flow Bonus" filler takes whatever is left.
        filler_needed = progression_count - len(itempool)
        if filler_needed > 0:
            extras = []

            req_solve = self.options.solve_random_pipe_count.value
            req_skip = self.options.skip_puzzle_count.value
            req_useful = req_solve + req_skip
            if req_useful <= filler_needed:
                n_solve, n_skip = req_solve, req_skip
            else:
                # Overflow: distribute the whole pool by the requested ratio (skip gets the remainder
                # so the two always sum to exactly filler_needed).
                n_solve = round(filler_needed * req_solve / req_useful)
                n_skip = filler_needed - n_solve
            extras += ["Solve Random Pipe"] * n_solve
            extras += ["Skip Puzzle"] * n_skip

            remaining = filler_needed - n_solve - n_skip
            trap_pct = self.options.trap_percentage.value
            num_traps = min(round(remaining * trap_pct / 100), remaining)
            trap_names = list(ITEMS_TRAPS.keys())
            for _ in range(num_traps):
                extras.append(self.random.choice(trap_names))

            extras += ["Flow Bonus"] * (remaining - num_traps)

            for name in extras:
                if name in ITEMS_TRAPS:
                    itempool.append(self.create_item(name, ItemClassification.trap))
                elif name in ITEMS_USEFUL:
                    itempool.append(self.create_item(name, ItemClassification.useful))
                else:
                    itempool.append(self.create_item("Flow Bonus"))

        # Add the completed pool to the multiworld itempool.
        multiworld.itempool += itempool

    def create_regions(self):

        from .Regions import create_apflowfree_regions
        create_apflowfree_regions(self.multiworld, self.player)

    def set_rules(self):
        apply_rules(self.multiworld, self.player)

    def fill_slot_data(self):
        import random

        player = self.player

        # Retrieve option values from the multiworld options.
        num_levels = self.options.levels.value
        stages_per_level = self.options.stages_per_level.value
        stage_sanity = self.options.stage_sanity.value
        strict_mode = self.options.strict_mode.value
        goal = self.options.goal.value
        goal_percentage = self.options.goal_percentage.value

        # Board-size knobs (color pairs per board + ramp shape). Clamp so min <= max.
        min_pairs = min(self.options.min_pairs.value, self.options.max_pairs.value)
        max_pairs = max(self.options.min_pairs.value, self.options.max_pairs.value)
        difficulty_curve = self.options.difficulty_curve.current_key

        # How many levels are unlocked from the start (clamped to the number of levels).
        starting_levels = min(self.options.starting_levels.value, num_levels)

        # Generate a seed for each stage within each level.
        seeds = {}
        for level in range(1, num_levels + 1):
            level_name = f"Level {level}"
            # Generate a list of random seeds for the given number of stages.
            seeds[level_name] = [random.randint(100000000, 999999999) for _ in range(stages_per_level)]

        # Format the slot data in the expected structure.
        slot_data = {
            'player': player,
            'goal': goal,
            'goal_percentage': goal_percentage,
            'number_of_levels': num_levels,
            'stages_per_level': stages_per_level,
            'stage_sanity': stage_sanity,
            'strict_mode': strict_mode,
            'starting_levels': starting_levels,
            'min_pairs': min_pairs,
            'max_pairs': max_pairs,
            'difficulty_curve': difficulty_curve,
            'death_link': bool(self.options.death_link.value),
            'seeds': seeds
        }
        return slot_data