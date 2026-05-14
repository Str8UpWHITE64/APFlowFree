from worlds.AutoWorld import World
from BaseClasses import Item, ItemClassification, MultiWorld
from .Items import ITEMS, ITEMS_B, ITEMS_C, ITEMS_FILLER, APFlowFreeItem
from .Locations import MAIN_LEVEL_COMPLETION_DICT, SECONDARY_LEVEL_COMPLETION_DICT, INDIVIDUAL_STAGE_COMPLETION_DICT
from .Options import APFlowFreeOptions
from .Rules import apply_rules

import sys

sys.stdout = open("apflowfree_debug_log.txt", "w")
sys.stderr = sys.stdout

class APFlowFreeWorld(World):
    game = "APFlowFree"
    options_dataclass = APFlowFreeOptions
    options = APFlowFreeOptions

    # Create a mapping from item names to their unique IDs
    item_name_to_id = {name: data[0] for name, data in ITEMS.items()}
    item_name_to_id.update({name: data[0] for name, data in ITEMS_B.items()})
    item_name_to_id.update({name: data[0] for name, data in ITEMS_C.items()})
    item_name_to_id.update({name: data[0] for name, data in ITEMS_FILLER.items()})

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

        if stage_sanity == 1:
            # Build a list of stage item names for the selected levels.
            selected_names = [f"Level {i} Stages" for i in range(2, num_levels + 1)]

        elif stage_sanity == 2:
            for i in range(2, num_levels + 1):
                selected_names.append(f"Level {i} Stages First Half")
                selected_names.append(f"Level {i} Stages Second Half")

        elif stage_sanity == 3:
            for i in range(2, num_levels + 1):
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

        # Add filler items to the end of the itempool until it reaches the desired count.
        while len(itempool) < progression_count:
            filler_item = self.create_item("Flow Bonus")  # uses ID & classification from ITEMS_FILLER
            itempool.append(filler_item)

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
            'number_of_levels': num_levels,
            'stages_per_level': stages_per_level,
            'stage_sanity': stage_sanity,
            'strict_mode': strict_mode,
            'seeds': seeds
        }
        return slot_data