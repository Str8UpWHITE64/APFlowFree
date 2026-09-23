from BaseClasses import ItemClassification
from test.bases import WorldTestBase
from test.general import setup_solo_multiworld
from worlds.AutoWorld import AutoWorldRegister


class FlowTestBase(WorldTestBase):
    game = "APFlowFree"


class TestSanity2Check2NeedsBothHalves(FlowTestBase):
    options = {"stage_sanity": 2, "levels": 5, "stages_per_level": 10}

    def test_check2_rule(self):
        loc = "Complete Level 3 Check 2"
        self.collect_by_name("Level 3 Stages Second Half")
        self.assertFalse(self.can_reach_location(loc), "Check 2 reachable with Second Half only")
        self.remove(self.get_items_by_name("Level 3 Stages Second Half"))
        self.collect_by_name("Level 3 Stages First Half")
        self.assertFalse(self.can_reach_location(loc), "Check 2 reachable with First Half only")
        self.collect_by_name("Level 3 Stages Second Half")
        self.assertTrue(self.can_reach_location(loc))


class TestCreateItemClassification(FlowTestBase):
    options = {"stage_sanity": 3, "levels": 4, "stages_per_level": 4, "trap_percentage": 50,
               "solve_random_pipe_count": 2, "skip_puzzle_count": 2}

    def test_classification_by_name(self):
        w = self.world
        self.assertEqual(w.create_item("Level 5 Stages").classification, ItemClassification.progression)
        self.assertEqual(w.create_item("Level 2 Stages First Half").classification, ItemClassification.progression)
        self.assertEqual(w.create_item("Level 3 Stage 2").classification, ItemClassification.progression)
        self.assertEqual(w.create_item("Fog Trap").classification, ItemClassification.trap)
        self.assertEqual(w.create_item("Skip Puzzle").classification, ItemClassification.useful)
        self.assertEqual(w.create_item("Flow Bonus").classification, ItemClassification.filler)

    def test_filler_name(self):
        self.assertEqual(self.world.get_filler_item_name(), "Flow Bonus")

    def test_victory_event_has_no_id(self):
        self.assertNotIn("Complete All Levels", self.world.location_name_to_id)
        self.assertIsNone(self.multiworld.get_location("Complete All Levels", self.player).address)

    def test_pool_classifications(self):
        pool = [i for i in self.multiworld.itempool if i.player == self.player]
        for it in pool:
            self.assertEqual(it.classification, self.world.item_name_to_classification[it.name], it.name)


class TestSeedsDeterministic(FlowTestBase):
    def test_same_seed_same_puzzles(self):
        wt = AutoWorldRegister.world_types[self.game]
        a = setup_solo_multiworld(wt, seed=12345)
        b = setup_solo_multiworld(wt, seed=12345)
        c = setup_solo_multiworld(wt, seed=54321)
        sa = a.worlds[1].fill_slot_data()["seeds"]
        self.assertEqual(sa, b.worlds[1].fill_slot_data()["seeds"])
        self.assertNotEqual(sa, c.worlds[1].fill_slot_data()["seeds"])


# Full generation (fill + beatability) across sanity x goal combinations.
for _san in (1, 2, 3):
    for _goal in (1, 2, 3):
        for _start in (1, 3):
            _name = f"TestGen_s{_san}_g{_goal}_start{_start}"
            globals()[_name] = type(_name, (FlowTestBase,), {
                "options": {"stage_sanity": _san, "goal": _goal, "starting_levels": _start,
                            "levels": 6, "stages_per_level": 5, "trap_percentage": 30},
            })
